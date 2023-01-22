function initNoteEvents() {
    $(".like-reaction-button").on("click", (event) => {
        react($(event.currentTarget), "like");
    });

    $(".dislike-reaction-button").on("click", (event) => {
        react($(event.currentTarget), "dislike");
    });

    $(".fake-reaction-button").on("click", (event) => {
        react($(event.currentTarget), "fake");
    });

    $(".share-note, .share-note > *").on('click', (event) => {

        const noteContainer = $(event.currentTarget).closest(".note-container");

        if (noteContainer.find(".share-note").attr("state") == "clicked") {
            return;
        }
        noteContainer.find(".share-note").attr("state", "clicked");

        const note_id = noteContainer.attr("note_id");
        navigator.clipboard.writeText(`${window.location.protocol}//${window.location.host}/nugget/${note_id}`)


        noteContainer.find(".share-note > i").css("visibility", "hidden");
        noteContainer.find(".share-note-message").css("visibility", "visible");

        let count = 0;
        const number_step = 3;
        const total_time = 600;
        const timer_step = Math.round(total_time / number_step);

        const progressbar = noteContainer.find(".share-note-message .progressbar-dot");
        progressbar.text(".".repeat(number_step));

        const shareAnimation = () => {
            if (count < number_step) {

                progressbar.text(progressbar.text().slice(0, -1));

                count += 1;

                setTimeout(shareAnimation, timer_step);

            } else {
                noteContainer.find(".share-note > i").css("visibility", "visible");
                noteContainer.find(".share-note-message").css("visibility", "hidden");

                noteContainer.find(".share-note").attr("state", "");
            }
        }

        setTimeout(shareAnimation, timer_step);
    });
}


function setNote(noteElem, noteData) {

    noteElem.attr("note_id", noteData["id"]);

    noteElem.find(".note-title").text("#" + noteData["id"]);
    noteElem.find(".note-subtitle").text(noteData["date"]);

    noteElem.find(".note-content-header").html(noteData["content"]["header"]);
    noteElem.find(".note-content-body").html(noteData["content"]["body"]);
    noteElem.find(".note-content-footer").html(noteData["content"]["footer"]);

    noteElem.find(".like-reaction-button .reaction-counter-value").text(noteData["reactions"]["like"]);
    noteElem.find(".dislike-reaction-button .reaction-counter-value").text(noteData["reactions"]["dislike"]);
    noteElem.find(".fake-reaction-button .reaction-counter-value").text(noteData["reactions"]["fake"]);

}