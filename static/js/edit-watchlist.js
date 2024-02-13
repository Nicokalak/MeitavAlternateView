function getItem(item= "") {
    return "<li class='list-group-item border-0'>" +
        "<div class='input-group input-group-sm'>" +
        "<input type='text' class='form-control form-control-sm' value='" + item + "'>" +
        "<button class='btn btn-danger delete-item' type='button'><i class='fas fa-times'></i>" +
        "</button></div></li>";
}

$(document).ready(function(){
    let change = false;
    // Perform HTTP GET request to fetch list data
    $.get("watchList", function(data){
        // Populate the list in the modal with fetched data
        if(data && data.length > 0){
            var listItems = $("#listItems");
            listItems.empty(); // Clear existing items

            // Append fetched data to the list
            data.forEach(function(item){
                listItems.append(getItem(item));
            });
        }
    });

    // Add item button click event
    $("#addItemBtn").click(function(){
        $("#listItems").append(getItem());
    });

    // Delete item button click event
    $(document).on("click", ".delete-item", function(){
        $(this).closest("li").remove();
    });

    // Save changes button click event
    $("#saveChanges").click(function(){
        let updatedList = [];

        // Iterate through each input field in the list
        $("#listItems input[type='text']").each(function(){
            updatedList.push($(this).val()); // Add the value to the updated list
        });

       // Perform an HTTP POST request to save the updated list
        $.ajax({
            url: "watchList",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(updatedList),
            success: function(response) {
                console.log("Success:", response);
                change = true;
                $("#successMessage").text(response.message).show().delay(3000).fadeOut(); // Show success message for 3 seconds
            },
            error: function(xhr, status, error) {
                console.error("Error:", error);
            }
        });

        console.log("Updated list:", updatedList);
    });

    $('#editWatchListModal').on('hide.bs.modal', function (e) {
        if (change) {
            $('#table').bootstrapTable('refresh')
            console.log("watchlist changed");
        }
    })
});