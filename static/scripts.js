$(document).ready(function () {
    // Generate dropdown for due dates
    const generateDueDates = () => {
        const currentYear = new Date().getFullYear();
        const dueDates = [
            `April 15, ${currentYear}`,
            `June 15, ${currentYear}`,
            `September 15, ${currentYear}`,
            `January 15, ${currentYear + 1}`,
        ];
        const dueDateDropdown = $("#due_date");
        dueDateDropdown.empty();
        dueDates.forEach(date => dueDateDropdown.append(new Option(date, date)));
    };

    // Fetch and display records
    const fetchRecords = () => {
        $.get('/records', function (data) {
            let recordsHtml = `<table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Company</th>
                        <th>Amount</th>
                        <th>Payment Date</th>
                        <th>Status</th>
                        <th>Due Date</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>`;
            data.forEach(record => {
                recordsHtml += `<tr>
                    <td>${record.id}</td>
                    <td>${record.company}</td>
                    <td>${record.amount}</td>
                    <td>${record.payment_date || "NA"}</td>
                    <td>${record.status}</td>
                    <td>${record.due_date}</td>
                    <td>
                        <button onclick="deleteRecord(${record.id})">Delete</button>
                    </td>
                </tr>`;
            });
            recordsHtml += `</tbody></table>`;
            $("#records").html(recordsHtml);
        });
    };

    // Save record
    $("#tax-form").on('submit', function (e) {
        e.preventDefault();
        const record = {
            company: $("#company").val(),
            amount: parseFloat($("#amount").val()),
            payment_date: $("#payment_date").val(),
            status: $("#status").val(),
            due_date: $("#due_date").val()
        };
        $.post('/record', JSON.stringify(record), fetchRecords, "json");
    });

    // Delete record
    window.deleteRecord = (id) => {
        $.ajax({
            url: `/record/${id}`,
            type: 'DELETE',
            success: fetchRecords
        });
    };

    generateDueDates();
    fetchRecords();
});
$(document).ready(function () {
    // Handle dropdown change for filtering
    $("#due_date").change(function () {
        const dueDate = $(this).val();

        // Send AJAX request to filter route
        $.ajax({
            url: "/filter",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ due_date: dueDate }),
            success: function (response) {
                // Update the records table
                let recordsHtml = "";
                response.records.forEach(record => {
                    recordsHtml += `
                        <tr>
                            <td>${record.id}</td>
                            <td>${record.company}</td>
                            <td>${record.amount}</td>
                            <td>${record.payment_date}</td>
                            <td>${record.status}</td>
                            <td>${record.due_date}</td>
                            <td>
                                <a href="/edit/${record.id}" class="btn btn-sm btn-warning">Edit</a>
                                <a href="/delete/${record.id}" class="btn btn-sm btn-danger">Delete</a>
                            </td>
                        </tr>`;
                });
                $("#records-table").html(recordsHtml);

                // Update the tax summary
                $("#tax-summary").html(`
                    <h4>Summary for ${dueDate || "All Due Dates"}</h4>
                    <p><strong>Total Amount:</strong> ${response.total_amount}</p>
                    <p><strong>Tax Rate:</strong> ${response.tax_rate}</p>
                    <p><strong>Tax Due:</strong> ${response.tax_due}</p>
                `);
            },
            error: function () {
                alert("An error occurred while filtering records.");
            }
        });
    });
});

function confirmDelete(recordId) {
    const userConfirmed = confirm("Are you sure you want to delete this record?");
    if (userConfirmed) {
        // Redirect to the delete route
        window.location.href = `/delete/${recordId}`;
    }
}

