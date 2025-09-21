$(document).ready(function(){
    let debounceTimeout;
    let currentRequest = null;

    $("#search-box").on("keyup", function(){
        clearTimeout(debounceTimeout);
        let query = $(this).val().trim();

        debounceTimeout = setTimeout(() => {
            if(query.length < 2){ // only search for 2+ chars
                $("#suggestions").hide();
                return;
            }

            // abort previous request if pending
            if(currentRequest) currentRequest.abort();

            currentRequest = $.ajax({
                url: "/search_suggestions/",
                data: {'query': query},
                dataType: 'json',
                success: function(data){
                    let suggestions = data.suggestions;
                    let html = '';
                    suggestions.forEach(function(item){
                        html += `<a href="/apps/?q=${encodeURIComponent(item)}" class="list-group-item list-group-item-action">${item}</a>`;
                    });
                    $("#suggestions").html(html).show();
                },
                error: function(xhr, status, error){
                    if(status !== "abort") $("#suggestions").hide();
                },
                complete: function(){
                    currentRequest = null;
                }
            });
        }, 200); // 200ms debounce
    });

    // Hide suggestions if clicked outside
    $(document).click(function(e){
        if(!$(e.target).closest("#search-box, #suggestions").length){
            $("#suggestions").hide();
        }
    });
});
