/*jslint vars: false, browser: true, nomen: true */
/*global _, jQuery, MOOC */

// Copyright 2012 Rooter Analysis S.L.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

jQuery(document).ready(function () {
    "use strict";

    (function ($) {
        var getCookie,
            csrftoken,
            removeStudent,
            re;

        getCookie = function (name) {
            var cookieValue = null,
                cookies,
                i,
                cookie;

            if (document.cookie && document.cookie !== '') {
                cookies = document.cookie.split(';');
                for (i = 0; i < cookies.length; i += 1) {
                    cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        };

        csrftoken = getCookie("csrftoken");

        $("#invite-student").typeahead({
            source: function (query, process) {
                $.getJSON("/api/v1/user/",
                    {
                        format: "json",
                        limit: 10,
                        first_name__istartswith: query,
                        email__icontains: query,
                        last_name__istartswith: query
                    },
                    function (data, textStatus, jqXHR) {
                        process(_.map(data.objects, function (user) {
                            var name = "";
                            if (user.first_name || user.last_name) {
                                name = user.first_name + " " + user.last_name + ", ";
                            }
                            return name + user.email +" (" + user.id + ")";
                        }));
                    });
            },
            minLength: 1
        });

        removeStudent = function (evt) {
            var row = $(evt.target).parent().parent(),
                id = parseInt($(row.children()[0]).text(), 10),
                email = $(row.children()[2]).text();

            if (id < 0) {
                id = email;
            }

            $.ajax(MOOC.basePath + id + "/", {
                headers: {
                    "X-CSRFToken": csrftoken
                },
                type: "DELETE",
                success: function (data, textStatus, jqXHR) {
                    row.remove();
                    $("#removed.alert-success").show();
                    setTimeout(function () {
                        $(".alert-success").hide();
                    }, MOOC.alertTime);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    $("#generic.alert-error").show();
                    setTimeout(function () {
                        $(".alert-error").hide();
                        $(".alert-warning").hide();
                    }, MOOC.alertTime);
                }
            });
        };

        $("table .icon-remove").click(removeStudent);

        $("#invite-student").next().click(function (evt) {
            evt.preventDefault();
            evt.stopPropagation();
            var data = $("#invite-student").val(),
                idxA,
                idxB;

            $("#invite-student").val("");
            // Extract id from name
            idxA = data.lastIndexOf('(');
            idxB = data.lastIndexOf(')');
            if (idxA > 0 && idxB > 0) {
                data = data.substring(idxA + 1, idxB);
            } else {
                data = ""; // Invalid
            }

            $.ajax(MOOC.basePath + "enrol", {
                data: {
                    data: data
                },
                headers: {
                    "X-CSRFToken": csrftoken
                },
                dataType: "json",
                type: "POST",
                success: function (data, textStatus, jqXHR) {
                    var html = "<tr><td class='hide'>" + data.id + "</td>" +
                            "<td>"+ data.gravatar +"</td><td>" + data.name + "</td>" +
                            "<td>"+ data.email +"</td>"+
                            "<td class='membership'>";
                    if (data.is_owner) {
                        html += "<span class='label label-inverse'>" +
                            MOOC.owner + "</span>";
                    } else if (data.is_teacher) {
                        html += "<span class='label label-success'>" +
                            MOOC.teacher + "</span>";
                    } else if (data.institutions) {
                        if (data.is_member) {
                            html += "<span class='label label-info'>" +
                                MOOC.is_member + "</span>";
                        } else {
                            html += "<span class='label label-warning'>" +
                                MOOC.is_not_member + "</span>";
                        }
                    }
                    html += "</td><td class='align-right'>" +
                            "<i class='icon-remove pointer'></i></td></r>";
                    $("table > tbody").append(html);
                    $("table .icon-remove").off("click").click(removeStudent);
                    $("#added.alert-success").show();
                    setTimeout(function () {
                        $(".alert-success").hide();
                    }, MOOC.alertTime);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    $("#" + jqXHR.status).show();
                    setTimeout(function () {
                        $(".alert-error").hide();
                        $(".alert-warning").hide();
                    }, MOOC.alertTime);
                }
            });
        });

        $("#reload").click(function () {
            window.location.reload(true);
        });
    }(jQuery));
});
