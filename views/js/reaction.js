
$(window).on("load", () => {
    $('.reactions-container-loader').css('display', 'none');
    $('.material-symbols-outlined').css('opacity', '1');
    $('.reactions-container').css('opacity', '1');
});


function react(reactionElem, type) {

    const reaction_container_elem = reactionElem.closest(".reactions-container");
    if (reaction_container_elem.attr("state") == "loading") {
        return;
    }

    const noteId = reactionElem.closest(".note-container").attr("note_id");
    const operation = (reactionElem.attr("reacted") == "false") ? "add" : "remove";

    const data = {
        "operation": operation,
    };

    setLoading("reactions-container", true);
    reaction_container_elem.attr("state", "loading");

    $.post(`/api/note/${noteId}/reaction/${type}`, { data: JSON.stringify(data) }, (response_data) => {

        setLoading("reactions-container", false);
        reaction_container_elem.attr("state", "");

        if (response_data["error"] === true) {
            console.error(response_data);

            Swal.fire({
                icon: 'error',
                title: 'An error occurred',
                text: response_data["error_msg"],
            });
        } else {
            reactionElem.find("i").toggleClass("press", 1000);
            reactionElem.find("span").toggleClass("press", 1000);

            var counterElem = reactionElem.find('.reaction-counter-value');
            if (operation == "add") {
                counterElem.text(parseInt(counterElem.text()) + 1);
            } else {
                counterElem.text(parseInt(counterElem.text()) - 1);
            }

            reactionElem.attr("reacted", (reactionElem.attr("reacted") == "false") ? "true" : "false");
        }

    }).fail(function (xhr, status, error) {
        console.error(xhr, status, error);

        setLoading("reactions-container", false);
        reaction_container_elem.attr("state", "");

        Swal.fire({
            icon: 'error',
            title: 'An error occurred',
            html: xhr.responseText,
        });
    });

}
