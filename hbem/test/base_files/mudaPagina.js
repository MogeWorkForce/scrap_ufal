// Uso:
//     onclick="return mudaPagina(valor, limite);"
//     onkeypress="if (teclaEnter(event)) return mudaPagina(valor, limite);"

function mudaPagina(valor, limite)
{
    if (isNaN(valor) || (valor < 1) || (valor > limite)) {
       alert('Página inválida.');
       return false;
    }

    // remove a eventual âncora
    var urlAtual = window.location.href;
    var posAncora = urlAtual.indexOf("#");
    if (posAncora != -1) {
        urlAtual = urlAtual.substring(0, posAncora);
    }

    // inclui ou muda o parâmetro "pagina"
    var posPagina = urlAtual.indexOf("pagina=");
    var urlNova;
    if (posPagina == -1) {
        urlNova = urlAtual + (urlAtual.indexOf("?") == -1 ? "?" : "&") + "pagina=" + valor;
    }
    else {
        urlNova = urlAtual.substring(0, posPagina) + "pagina=" + valor;
        var posDepois = urlAtual.indexOf("&", posPagina);
        if (posDepois != -1) {
            urlNova += urlAtual.substring(posDepois);
        }
    }

    // acrescenta a âncora "paginacao" para ir direto para a paginação sobre a tabela
    urlNova += "#paginacao";

    if (urlNova != urlAtual) {
        window.location.href = urlNova;
    }
    return false;
}

function teclaEnter(evento)
{
	if (window.event) {
        // Internet Explorer
        return (window.event.keyCode == 13);
    }
	else if (evento) {
        // Firefox
        return (evento.which == 13);
    }
	else {
        return false;
    }
}
