(function ($) {
  init = function () {
    var drglearningHost = $("#drglearning-host").val();
        urlToEmbed = $("#career-url").val(),
        iframe = $("#career-iframe"),
        title = $("#career-title");

    $("a.career-id").each(function (e) {
      var $this = $(this);
      $this.on("click", function (elto) {
        var careerId = $this.data("career-id"),
            src = urlToEmbed + careerId +"&import="+ document.location.origin +"#"+ encodeURIComponent(document.location.href);
        title.text($this.text());
        iframe.attr("src", src);
        return false;
      });
    });

    XD.receiveMessage(function (message) {
      if (message.origin !== drglearningHost) {
        return;
      }
      if (message.data == "ready") {
        // XD.postMessage(user_code, src, frames[0]);
        console.log(message.data);
      }
    }, drglearningHost);

    $("a.career-id:first").click();
  };
  $(document).ready(init);
})(jQuery);
