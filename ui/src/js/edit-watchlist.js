function getItem(item = {}) {
    const symbol = item.symbol || "";
    const qty = item.qty !== undefined && item.qty !== null ? item.qty : "";
    const cost = item.cost !== undefined && item.cost !== null ? item.cost : "";
    const hasExtra = (qty !== "" && qty > 0) || (cost !== "" && cost > 0);
    const toggleBtnClass = hasExtra ? "btn-outline-primary" : "btn-outline-secondary";
    const toggleBtnTitle = hasExtra ? "Hide Qty & Cost" : "Set Qty & Cost";

    return (
        "<li class='list-group-item border rounded p-2 mb-2 bg-body-tertiary watchlist-item-row shadow-sm'>" +
        "<div class='d-flex align-items-center gap-2'>" +
        "<div class='flex-grow-1'>" +
        "<div class='input-group input-group-sm'>" +
        "<span class='input-group-text px-2'><i class='fas fa-tag text-muted'></i></span>" +
        "<input type='text' class='form-control form-control-sm text-uppercase fw-semibold watchlist-symbol' placeholder='Symbol' value='" + symbol + "' autocomplete='off' autocapitalize='characters'>" +
        "</div>" +
        "</div>" +
        "<div class='d-flex gap-1 flex-shrink-0'>" +
        "<button class='btn btn-sm " + toggleBtnClass + " toggle-item-details' type='button' title='" + toggleBtnTitle + "' aria-expanded='false'>" +
        "<i class='fas fa-sliders-h'></i>" +
        "</button>" +
        "<button class='btn btn-sm btn-outline-danger remove-item' type='button' title='Remove'>" +
        "<i class='fas fa-trash-alt'></i>" +
        "</button>" +
        "</div>" +
        "</div>" +
        "<div class='d-flex gap-2 mt-2 watchlist-extra-fields d-none'>" +
        "<div class='flex-fill'>" +
        "<div class='input-group input-group-sm'>" +
        "<span class='input-group-text px-2'>Qty</span>" +
        "<input type='number' min='0' step='1' class='form-control form-control-sm px-2 watchlist-qty' placeholder='0' value='" + qty + "'>" +
        "</div>" +
        "</div>" +
        "<div class='flex-fill'>" +
        "<div class='input-group input-group-sm'>" +
        "<span class='input-group-text px-2'>Cost</span>" +
        "<input type='number' min='0' step='any' class='form-control form-control-sm px-2 watchlist-cost' placeholder='0.00' value='" + cost + "'>" +
        "</div>" +
        "</div>" +
        "</div>" +
        "</li>"
    );
}

function checkEmptyState() {
    if ($("#listItems .watchlist-item-row").length === 0) {
        $("#watchlistEmptyState").show();
    } else {
        $("#watchlistEmptyState").hide();
    }
}

$(document).ready(function () {
    let change = false;

    function loadWatchlist() {
        $.get("watchList", function (data) {
            var listItems = $("#listItems");
            listItems.empty();
            if (data && data.length > 0) {
                data.forEach(function (item) {
                    listItems.append(getItem(item));
                });
            }
            checkEmptyState();
        }).fail(function (xhr, status, error) {
            console.error("Failed to load watchlist:", error);
        });
    }

    // Initial load
    loadWatchlist();

    // Toggle per-row extra fields inline
    $(document).on("click", ".toggle-item-details", function () {
        const row = $(this).closest(".watchlist-item-row");
        const extraFields = row.find(".watchlist-extra-fields");
        const toggleBtn = $(this);
        const isHidden = extraFields.hasClass("d-none");

        if (isHidden) {
            extraFields.removeClass("d-none");
            toggleBtn.removeClass("btn-outline-secondary btn-outline-primary").addClass("btn-primary");
            toggleBtn.attr("aria-expanded", "true");
        } else {
            extraFields.addClass("d-none");
            const qtyVal = parseInt(row.find(".watchlist-qty").val().trim(), 10);
            const costVal = parseFloat(row.find(".watchlist-cost").val().trim());
            const hasValues = (!isNaN(qtyVal) && qtyVal > 0) || (!isNaN(costVal) && costVal > 0);

            toggleBtn.removeClass("btn-primary").addClass(hasValues ? "btn-outline-primary" : "btn-outline-secondary");
            toggleBtn.attr("aria-expanded", "false");
        }
    });

    // Add item button click event
    $("#addItemBtn").click(function () {
        $("#listItems").append(getItem());
        checkEmptyState();
        $("#listItems .watchlist-item-row:last-child .watchlist-symbol").focus();
    });

    // Delete item button click event
    $(document).on("click", ".delete-item", function () {
        $(this).closest(".watchlist-item-row").remove();
        checkEmptyState();
    });

    // Save changes button click event
    $("#saveChanges").click(function () {
        let updatedList = [];

        $("#listItems .watchlist-item-row").each(function () {
            let symbol = $(this).find(".watchlist-symbol").val().trim().toUpperCase();
            if (!symbol) return;
            let qtyVal = $(this).find(".watchlist-qty").val().trim();
            let costVal = $(this).find(".watchlist-cost").val().trim();

            let quantity = qtyVal === "" ? 0 : parseInt(qtyVal, 10);
            let cost = costVal === "" ? 0.0 : parseFloat(costVal);

            updatedList.push({
                symbol: symbol,
                quantity: isNaN(quantity) ? 0 : Math.max(0, quantity),
                cost: isNaN(cost) ? 0.0 : Math.max(0.0, cost),
            });
        });

        let saveBtn = $(this);
        saveBtn.prop("disabled", true);

        $.ajax({
            url: "watchList",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(updatedList),
            success: function (response) {
                change = true;
                $("#errorMessage").hide();
                $("#successMessage").text(response.message || "Saved successfully").fadeIn().delay(3000).fadeOut();
            },
            error: function (xhr, status, error) {
                console.error("Error saving watchlist:", error);
                $("#successMessage").hide();
                let errMsg = (xhr.responseJSON && xhr.responseJSON.detail) || error || "Failed to save";
                $("#errorMessage").text("Error: " + errMsg).fadeIn().delay(4000).fadeOut();
            },
            complete: function () {
                saveBtn.prop("disabled", false);
            },
        });
    });

    $("#editWatchListModal").on("show.bs.modal", function () {
        loadWatchlist();
    });

    $("#editWatchListModal").on("hide.bs.modal", function () {
        if (change) {
            $("#table").bootstrapTable("refresh");
            console.log("watchlist changed, refreshing table");
            change = false;
        }
    });
});
