function setLoading(className, loading) {
    $("." + className + "-loader").css("display", loading ? "" : "none");

    if (className == "page") {
        $(".notes-viewer").css("visibility", "visible");
    }
}

function setUrlArg(url, name, value) {
    if (value === null) {
        url.searchParams.delete(name);
        return;
    }

    url.searchParams.set(name, value);
}


function getRouteParameter(index, uri=null) {
    if (uri==null) {
        uri = location.pathname;
    }

    const list = uri.split('/');

    if (index < 0) {
        index = list.length + index;
    } else {
        index += 1; // first element of list is empty
    }

    return list[index];
}