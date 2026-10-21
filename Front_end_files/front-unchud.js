// front-end for unchud
        const calendarGrid = document.getElementById("calendarGrid");
        const monthYear = document.getElementById("monthYear");
        const calendarStatus = document.getElementById("calendarStatus");

        // Map each YYYY-MM-DD date to the assignments due on that date.
        let assignmentsByDate = {};

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
                                    dueTime
                                });
                            }
                        }
                    }
                }

                assignmentsByDate = byDate;
                calendarStatus.textContent = "";
                renderCalendar();
            } catch (error) {
                console.error("Could not load assignments:", error);
                calendarStatus.textContent =
                    "Unable to load assignments. Make sure FastAPI is running and GET /assignments is available.";
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

                    label.appendChild(title);
                    label.appendChild(details);
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

        // Display the calendar immediately, then populate it from saved data.
        renderCalendar();
        loadAssignments();

        // Update assignments when the user returns to this page/tab.
        window.addEventListener("focus", loadAssignments);

        // An assignment form on this page can call loadAssignments()
        // after a successful POST /add_assignment request.