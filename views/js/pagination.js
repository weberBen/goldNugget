function clearPaginationUrl(url, clearPageSize = false) {

    setUrlArg(url, "pageNumber", null);
    setUrlArg(url, "paginationStart", null);

    if (clearPageSize) {
        setUrlArg("pageSize", null);
    }
}