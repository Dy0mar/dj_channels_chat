function create_socket(path){
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const host = ws_scheme
      + '://'
      + window.location.host
      + "/"
      + path;
    return new WebSocket(host);
}
