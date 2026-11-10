// front-end for unchud
        const calendarGrid = document.getElementById("calendarGrid");
        const monthYear = document.getElementById("monthYear");
        const calendarStatus = document.getElementById("calendarStatus");

        // Map each YYYY-MM-DD date to the assignments due on that date.
        let assignmentsByDate = {};

        // Class names the user has already saved (used by the Add popup's dropdown).
        let classNames = [];

        // Show a message under the calendar header (green for success, red for errors).
        // The message is mirrored inside the Assignments popup while it is open.
        function setStatus(message, isSuccess = false) {
            for (const el of [calendarStatus, document.getElementById("listMessage")]) {
                el.textContent = message;
                el.classList.toggle("success", isSuccess);
            }
        }

        // Local date as YYYY-MM-DD (toISOString() would use UTC and can be off by a day).
        function toDateString(date) {
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}` +
                `-${String(date.getDate()).padStart(2, "0")}`;
        }

        // Fetch the saved data through FastAPI (NOT directly from the JSON file).
        async function loadAssignments() {
            try {
                const response = await fetch("/assignments");
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                const savedAssignments = await response.json();
                const byDate = {};

                // Backend format: { class_name: { due_date: { due_time: [names] } } }
                for (const [className, dates] of Object.entries(savedAssignments)) {
                    for (const [dueDate, times] of Object.entries(dates)) {
                        for (const [dueTime, names] of Object.entries(times)) {
                            if (!Array.isArray(names)) continue;
                            if (!byDate[dueDate]) byDate[dueDate] = [];

                            for (const name of names) {
                                byDate[dueDate].push({
                                    className,
                                    name,
                                    dueDate,
                                    dueTime
                                });
                            }
                        }
                    }
                }

                assignmentsByDate = byDate;
                classNames = Object.keys(savedAssignments).sort();
                setStatus("");
                renderCalendar();
                if (listDialog.open) renderAssignmentList();
            } catch (error) {
                console.error("Could not load assignments:", error);
                setStatus(
                    "Unable to load assignments. Make sure FastAPI is running and GET /assignments is available."
                );
            }
        }

        let currentDate = new Date();
        currentDate.setDate(1);

        function renderCalendar() {
            const year = currentDate.getFullYear();
            const month = currentDate.getMonth();

            // Display current month and year
            monthYear.textContent = currentDate.toLocaleString(
                "default",
                { month: "long", year: "numeric" }
            );

            // Clear old days but keep weekday headers
            while (calendarGrid.children.length > 7) {
                calendarGrid.lastChild.remove();
            }

            // First weekday of the month
            const firstDay = new Date(year, month, 1).getDay();

            // Number of days in the month
            const daysInMonth = new Date(
                year, month + 1, 0
            ).getDate();

            // Add empty cells before first day
            for (let i = 0; i < firstDay; i++) {
                const emptyCell = document.createElement("div");
                calendarGrid.appendChild(emptyCell);
            }

            // Generate calendar days
            for (let day = 1; day <= daysInMonth; day++) {
                const dayCell = document.createElement("div");

                dayCell.classList.add("day");
                dayCell.textContent = day;

                // Store date for future assignments
                const dateString =
                    `${year}-${String(month + 1).padStart(2, "0")}` +
                    `-${String(day).padStart(2, "0")}`;

                dayCell.dataset.date = dateString;

                // Put each matching assignment inside its due-date cell.
                for (const assignment of (assignmentsByDate[dateString] || [])) {
                    const label = document.createElement("div");
                    label.classList.add("calendar-assignment");

                    const title = document.createElement("span");
                    title.classList.add("assignment-title");
                    title.textContent = assignment.name;

                    const details = document.createElement("span");
                    details.classList.add("assignment-details");
                    details.textContent = `${assignment.className} · ${assignment.dueTime}`;

                    const doneButton = document.createElement("button");
                    doneButton.type = "button";
                    doneButton.classList.add("mark-done");
                    doneButton.textContent = "✓";
                    doneButton.title = "Mark complete";
                    doneButton.setAttribute("aria-label", `Mark ${assignment.name} complete`);
                    doneButton.addEventListener("click", () => markAssignment(assignment));

                    label.appendChild(title);
                    label.appendChild(details);
                    label.appendChild(doneButton);
                    dayCell.appendChild(label);
                }

                // Highlight today's date
                const today = new Date();

                if (
                    day === today.getDate() &&
                    month === today.getMonth() &&
                    year === today.getFullYear()
                ) {
                    dayCell.classList.add("today");
                }

                calendarGrid.appendChild(dayCell);
            }
        }

        // Previous Month
        document.getElementById("prevMonth").addEventListener(
            "click",
            () => {
                currentDate.setMonth(currentDate.getMonth() - 1);
                renderCalendar();
            }
        );

        // Next Month
        document.getElementById("nextMonth").addEventListener(
            "click",
            () => {
                currentDate.setMonth(currentDate.getMonth() + 1);
                renderCalendar();
            }
        );

        // ---------- Mark assignment complete ----------
        // Sends the exact stored class/date/time/name so the backend lookup always matches.
        async function markAssignment(assignment) {
            if (!confirm(`Mark "${assignment.name}" for ${assignment.className} complete?`)) return;

            try {
                const response = await fetch("/mark_assignment", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        due_date: assignment.dueDate,
                        due_time: assignment.dueTime,
                        class_name: assignment.className,
                        assignment_name: assignment.name
                    })
                });
                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const result = await response.json();
                await loadAssignments();
                setStatus(result.message, result.success);
            } catch (error) {
                console.error("Could not mark assignment:", error);
                // Reload anyway: the backend may have changed its data before failing.
                await loadAssignments();
                setStatus("Server error marking assignment.");
            }
        }

        // ---------- Current Assignments popup ----------
        const listDialog = document.getElementById("listDialog");
        const assignmentList = document.getElementById("assignmentList");

        // "02:30 PM" -> minutes since midnight, for sorting and past-due checks.
        function timeToMinutes(dueTime) {
            const match = /^(\d{1,2}):(\d{2})\s*(AM|PM)$/i.exec(dueTime.trim());
            if (!match) return 0;
            const hour = Number(match[1]) % 12 + (match[3].toUpperCase() === "PM" ? 12 : 0);
            return hour * 60 + Number(match[2]);
        }

        function dueDateTime(assignment) {
            const [y, m, d] = assignment.dueDate.split("-").map(Number);
            const minutes = timeToMinutes(assignment.dueTime);
            return new Date(y, m - 1, d, Math.floor(minutes / 60), minutes % 60);
        }

        function renderAssignmentList() {
            const pending = Object.values(assignmentsByDate)
                .flat()
                .sort((a, b) => dueDateTime(a) - dueDateTime(b));

            assignmentList.replaceChildren();

            if (pending.length === 0) {
                const empty = document.createElement("li");
                empty.classList.add("empty");
                empty.textContent = "No pending assignments 🎉";
                assignmentList.appendChild(empty);
                return;
            }

            const now = new Date();
            for (const assignment of pending) {
                const item = document.createElement("li");
                if (dueDateTime(assignment) < now) item.classList.add("past-due");

                const info = document.createElement("div");
                const title = document.createElement("span");
                title.classList.add("assignment-title");
                title.textContent = assignment.name;
                const details = document.createElement("span");
                details.classList.add("assignment-details");
                details.textContent =
                    `${assignment.className} · ${assignment.dueDate} · ${assignment.dueTime}`;
                info.appendChild(title);
                info.appendChild(details);

                const doneButton = document.createElement("button");
                doneButton.type = "button";
                doneButton.textContent = "Mark complete";
                doneButton.addEventListener("click", () => markAssignment(assignment));

                item.appendChild(info);
                item.appendChild(doneButton);
                assignmentList.appendChild(item);
            }
        }

        document.getElementById("openListDialog").addEventListener("click", () => {
            renderAssignmentList();
            listDialog.showModal();
        });
        document.getElementById("closeList").addEventListener("click", () => listDialog.close());

        // ---------- Add Assignment popup ----------
        const addDialog = document.getElementById("addDialog");
        const addForm = document.getElementById("addForm");
        const classSelect = document.getElementById("classSelect");
        const newClassField = document.getElementById("newClassField");
        const newClassInput = document.getElementById("newClassInput");
        const assignmentNameInput = document.getElementById("assignmentNameInput");
        const dueDateInput = document.getElementById("dueDateInput");
        const hourInput = document.getElementById("hourInput");
        const minuteInput = document.getElementById("minuteInput");
        const ampmSelect = document.getElementById("ampmSelect");
        const addMessage = document.getElementById("addMessage");

        const NEW_CLASS = "__new__";

        function addOption(select, value, text = value) {
            const option = document.createElement("option");
            option.value = value;
            option.textContent = text;
            select.appendChild(option);
        }

        // Hour/minute boxes accept digits only.
        for (const input of [hourInput, minuteInput]) {
            input.addEventListener("input", () => {
                input.value = input.value.replace(/\D/g, "");
            });
        }

        // Jump to the minute box once two hour digits are typed.
        hourInput.addEventListener("input", () => {
            if (hourInput.value.length === 2) {
                minuteInput.focus();
                minuteInput.select();
            }
        });

        // Backend expects "HH:MM AM/PM", zero-padded, e.g. "02:05 PM".
        function formatTime(hour, minute, ampm) {
            return `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")} ${ampm}`;
        }

        function updateNewClassField() {
            const isNew = classSelect.value === NEW_CLASS;
            newClassField.hidden = !isNew;
            if (isNew) newClassInput.focus();
        }

        function openAddDialog() {
            // Rebuild the class list from the classes saved so far.
            classSelect.replaceChildren();
            for (const name of classNames) addOption(classSelect, name);
            addOption(classSelect, NEW_CLASS, "+ Add new class");

            addForm.reset();
            newClassInput.value = "";
            dueDateInput.value = toDateString(new Date());
            hourInput.value = "11";
            minuteInput.value = "59";
            ampmSelect.value = "PM";
            addMessage.textContent = "";

            addDialog.showModal();
            updateNewClassField();
            if (classSelect.value !== NEW_CLASS) assignmentNameInput.focus();
        }

        async function submitAddForm(event) {
            event.preventDefault();

            const className = classSelect.value === NEW_CLASS
                ? newClassInput.value.trim()
                : classSelect.value;
            const assignmentName = assignmentNameInput.value.trim();

            if (!className) {
                addMessage.textContent = "Please enter a class name.";
                return;
            }
            if (!assignmentName) {
                addMessage.textContent = "Please enter an assignment name.";
                return;
            }
            if (!dueDateInput.value) {
                addMessage.textContent = "Please pick a due date.";
                return;
            }

            const hour = Number(hourInput.value);
            const minute = Number(minuteInput.value);
            if (hourInput.value === "" || hour < 1 || hour > 12) {
                addMessage.textContent = "Hour must be between 1 and 12.";
                hourInput.focus();
                return;
            }
            if (minuteInput.value === "" || minute > 59) {
                addMessage.textContent = "Minute must be between 00 and 59.";
                minuteInput.focus();
                return;
            }

            try {
                const response = await fetch("/add_assignment", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        due_date: dueDateInput.value,
                        due_time: formatTime(hour, minute, ampmSelect.value),
                        class_name: className,
                        assignment_name: assignmentName
                    })
                });
                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const result = await response.json();
                if (!result.success) {
                    addMessage.textContent = result.message;
                    return;
                }

                addDialog.close();
                await loadAssignments();
                setStatus(result.message, true);
            } catch (error) {
                console.error("Could not add assignment:", error);
                addMessage.textContent = "Server error adding assignment. Is FastAPI running?";
            }
        }

        document.getElementById("openAddDialog").addEventListener("click", openAddDialog);
        document.getElementById("cancelAdd").addEventListener("click", () => addDialog.close());
        classSelect.addEventListener("change", updateNewClassField);
        addForm.addEventListener("submit", submitAddForm);

        // Display the calendar immediately, then populate it from saved data.
        renderCalendar();
        loadAssignments();

        // Update assignments when the user returns to this page/tab.
        window.addEventListener("focus", loadAssignments);