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
