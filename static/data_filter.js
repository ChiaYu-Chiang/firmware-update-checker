$(function () {
    // 當品牌選單改變時，過濾型號選單
    $("#brand").change(function () {
        var brand = $(this).val();
        if (brand === "All") {
            $("#model option").show();
        } else {
            $("#model option").hide();
            $("#model option[value='']").show();
            $("#model option[data-brand='" + brand + "']").show();
        };
    });
});

var sortDirection = 1;
// 排序表格
function sortTable(columnIndex) {
    var table, rows, switching, i, x, y, shouldSwitch;
    table = document.getElementsByTagName("table")[0];
    switching = true;
    while (switching) {
        switching = false;
        rows = table.getElementsByTagName("tr");
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("td")[columnIndex];
            y = rows[i + 1].getElementsByTagName("td")[columnIndex];
            if (sortDirection == 1) {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            } else {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
    sortDirection = 1 - sortDirection; // 切換排序方向
}

// $(document).ready(function () {
//     $('#brand, #model, #importance, #search-input').change(function () {
//         var brand = $('#brand').val();
//         var model = $('#model').val();
//         var importance = $('#importance').val();
//         var search = $('#search-input').val();
//         var url = '/';
//         var params = {};
//         if (brand) {
//             params.brand = brand;
//         }
//         if (model) {
//             params.model = model;
//         }
//         if (importance) {
//             params.importance = importance;
//         }
//         if (search) {
//             params.search = search;
//         }
//         if (Object.keys(params).length) {
//             url += '?' + $.param(params);
//         }
//         $.get(url, function (data) {
//             $('#drivers-table').html($(data).find('#drivers-table').html());
//         });
//     });
// });

// 用戶輸入時，延遲 750 毫秒再發送請求
var timeoutId;
$('#brand, #model, #importance, #search-input').on('input', function () {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(function () {
        var brand = $('#brand').val();
        var model = $('#model').val();
        var importance = $('#importance').val();
        var search = $('#search-input').val();
        var url = '/';
        var params = {};
        if (brand) {
            params.brand = brand;
        }
        if (model) {
            params.model = model;
        }
        if (importance) {
            params.importance = importance;
        }
        if (search) {
            params.search = search;
        }
        if (Object.keys(params).length) {
            url += '?' + $.param(params);
        }
        $.get(url, function (data) {
            $('#drivers-table').html($(data).find('#drivers-table').html());
        });
    }, 750);
});

