/*jslint vars: false, browser: true, nomen: true */
/*global MOOC: true, Backbone, $, _, YT, async */

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

if (_.isUndefined(window.MOOC)) {
    window.MOOC = {};
}

MOOC.views = {};

MOOC.views.KQ_TITLE_MAX_LENGTH = 60;

MOOC.views.Unit = Backbone.View.extend({
    events: {
        "click li span.kq": "showKQ",
        "click li span.q": "showQ",
        "click li span.a": "showA"
    },

    render: function () {
        "use strict";
        var html = '<div class="accordion-inner kqContainer"><ol>', css_class = null;
        this.model.get("knowledgeQuantumList").each(function (kq) {
            css_class = MOOC.models.activity.hasKQ(kq.get('id')) ? ' label-info' : '';
            html += '<li id="kq' + kq.get("id") + '"><span class="kq label' + css_class + '" title="' + kq.get("title") + '">' + kq.truncateTitle(25) + '</span>';
            if (kq.has("question")) {
                html += ' <span class="q label">' + MOOC.trans.classroom.q + '</span> ';
                html += '/ <span class="a label">' + MOOC.trans.classroom.a + '</span>';
            }
            html += '</li>';
        });
        html += '</ol></div>';
        this.$el.html(html);
        return this;
    },

    showKQ: function (evt) {
        "use strict";
        var kq = $(evt.target).parent().attr("id").split("kq")[1];
        MOOC.router.navigate(this.id + "/kq" + kq, { trigger: true });
    },

    showQ: function (evt) {
        "use strict";
        var kq = $(evt.target).parent().attr("id").split("kq")[1];
        MOOC.router.navigate(this.id + "/kq" + kq + "/q", { trigger: true });
    },

    showA: function (evt) {
        "use strict";
        var kq = $(evt.target).parent().attr("id").split("kq")[1];
        MOOC.router.navigate(this.id + "/kq" + kq + "/a", { trigger: true });
    }
});

MOOC.views.unitViews = {};

MOOC.views.KnowledgeQuantum = Backbone.View.extend({
    render: function () {
        "use strict";
        var height = this.getVideoHeight(),
            player,
            html,
            unit,
            order,
            kq,
            kqObj,
            comments,
            supplementary;

        html = '<iframe id="ytplayer" width="100%" height="' + height + 'px" ';
        html += 'src="//www.youtube.com/embed/' + this.model.get("videoID");
        html += '?rel=0&origin=' + MOOC.host;
        html += '" frameborder="0" allowfullscreen></iframe>';
        $("#kq-video").html(html);

        $("#kq-q-buttons").addClass("hide");
        $("#kq-next-container").addClass("offset4");

        if (this.model.has("question")) {
            this.loadQuestionData();
        }
        this.repeatedlyCheckIfPlayer();

        $("#kq-title").html(this.model.truncateTitle(MOOC.views.KQ_TITLE_MAX_LENGTH));

        unit = MOOC.models.course.getByKQ(this.model.get("id"));
        this.setEventForNavigation("#kq-previous", unit, this.model, false);
        this.setEventForNavigation("#kq-next", unit, this.model, true);

        this.$el.parent().children().removeClass("active");
        this.$el.addClass("active");

        comments = this.model.get("teacher_comments") || '';
        $("#comments").html(comments);

        supplementary = this.model.get("supplementary_material") || '';
        supplementary += "<ul id='attachments'></ul>";
        $("#supplementary").html(supplementary);

        this.setupListernerFor(this.model, "attachmentList", _.bind(function () {
            this.model.get("attachmentList").each(function (attachment) {
                var view = new MOOC.views.Attachment({
                    model: attachment,
                    el: $("#supplementary").find("ul#attachments")[0]
                });
                view.render();
            });
        }, this));

        return this;
    },

    getVideoHeight: function () {
        "use strict";
        var width = $("#kq-video").css("width"),
            height;

        if (width.indexOf('p') > 0) {
            width = parseInt(width.split('p')[0], 10);
        } else {
            width = parseInt(width, 10);
        }
        height = Math.round((width * 6) / 10);
        if (height < 200) {
            height = 200;
        }

        return height;
    },

    setEventForNavigation: function (selector, unit, kq, next) {
        "use strict";
        var path = window.location.hash,
            order = kq.get("order"),
            getUrlForOtherKQ,
            target,
            url;

        getUrlForOtherKQ = function (position, answer) {
            var aux = unit.get("knowledgeQuantumList").getByPosition(position),
                url;
            if (_.isUndefined(aux)) {
                $(selector).addClass("disabled");
            } else {
                url = "unit" + unit.get("id") + "/kq" + aux.get("id");
                if (answer && aux.has("question")) {
                    url += "/a";
                }
                return url;
            }
        };

        $(selector).unbind("click");

        if (/#[\w\/]+\/q/.test(path)) { // Viewing question
            target = next ? "answer" : "same";
        } else if (/#[\w\/]+\/a/.test(path)) { // Viewing answer
            target = next ? "next" : "question";
        } else { // Viewing kq
            target = next ? "question" : "prev";
        }
        if (target === "question" && !kq.has("question")) {
            target = "next";
        }

        switch (target) {
        case "question":
            url = "unit" + unit.get("id") + "/kq" + kq.get("id") + "/q";
            break;
        case "answer":
            url = "unit" + unit.get("id") + "/kq" + kq.get("id") + "/a";
            break;
        case "next":
            url = getUrlForOtherKQ(order + 1, false);
            break;
        case "prev":
            url = getUrlForOtherKQ(order - 1, true);
            break;
        case "same":
            url = "unit" + unit.get("id") + "/kq" + kq.get("id");
            break;
        }

        if (_.isUndefined(url)) {
            $(selector).addClass("disabled");
        } else {
            $(selector).removeClass("disabled");
            $(selector).click(function (evt) {
                MOOC.router.navigate(url, { trigger: true });
            });
        }
    },

    player: null,

    repeatedlyCheckIfPlayer: function (callback) {
        "use strict";
        if (MOOC.YTready) {
            this.player = new YT.Player("ytplayer", {
                events: {
                    onStateChange: _.bind(this.loadQuestion, this)
                }
            });
            if (!_.isUndefined(callback)) {
                callback();
            }
        } else {
            _.delay(_.bind(this.repeatedlyCheckIfPlayer, this), 200, callback);
        }
    },

    setupListernerFor: function (model, property, callback) {
        "use strict";
        if (model.has(property)) {
            callback();
        } else {
            model.on("change", function (evt) {
                if (this.has(property)) {
                    this.off("change");
                    callback();
                }
            }, model);
        }
    },

    loadQuestionData: function () {
        "use strict";
        var kqObj = this.model;
        if (!kqObj.has("questionInstance")) {
            // Load Question Data
            MOOC.ajax.getResource(kqObj.get("question"), function (data, textStatus, jqXHR) {
                var question = new MOOC.models.Question({
                        id: data.id,
                        lastFrame: data.last_frame,
                        solution: data.solutionID,
                        use_last_frame: data.use_last_frame
                    });
                kqObj.set("questionInstance", question);
                // Load Options for Question
                MOOC.ajax.getOptionsByQuestion(question.get("id"), function (data, textStatus, jqXHR) {
                    var options = _.map(data.objects, function (opt) {
                        return new MOOC.models.Option(_.pick(opt, "id", "optiontype", "x", "y", "width", "height", "solution", "text"));
                    });
                    question.set("optionList", new MOOC.models.OptionList(options));
                });
                // Load Answer for Question
                MOOC.ajax.getAnswerByQuestion(question.get("id"), function (data, textStatus, jqXHR) {
                    var obj, replies, answer;
                    if (data.objects.length === 1) {
                        obj = data.objects[0];
                        replies = _.map(obj.replyList, function (reply) {
                            return new MOOC.models.Reply(_.pick(reply, "option", "value"));
                        });
                        answer = new MOOC.models.Answer({
                            id: question.get('id'),
                            date: obj.date,
                            replyList: new MOOC.models.ReplyList(replies)
                        });
                    } else {
                        answer = new MOOC.models.Answer({
                            date: null,
                            replyList: new MOOC.models.ReplyList([])
                        });
                    }
                    question.set("answer", answer);
                });
            });
        }
    },

    loadQuestion: function (evt) {
        "use strict";
        if (evt.data === YT.PlayerState.ENDED) {
            var model = this.model,
                toExecute;

            // Mark kq as "viewed"
            MOOC.models.activity.addKQ(String(model.get("id")), function () {
                var unit = MOOC.models.course.getByKQ(model),
                    view = MOOC.views.unitViews[unit.get("id")];

                view.render();
            });

            // We can't assume the question exists
            if (model.has("question")) {
                toExecute = [];

                if (!this.model.has("questionInstance")) {
                    toExecute.push(async.apply(this.setupListernerFor, this.model, "questionInstance"));
                }

                toExecute.push(_.bind(function (callback) {
                    var question = this.model.get("questionInstance");
                    this.setupListernerFor(question, "optionList", callback);
                }, this));

                toExecute.push(_.bind(function (callback) {
                    var question = this.model.get("questionInstance");
                    this.setupListernerFor(question, "answer", callback);
                }, this));

                toExecute.push(_.bind(function (callback) {
                    var question = this.model.get("questionInstance"),
                        view = MOOC.views.questionViews[question.get("id")],
                        data = {
                            kq: this.model.get("id")
                        },
                        path = window.location.hash.substring(1),
                        unit = MOOC.models.course.getByKQ(this.model);

                    $("#kq-title").html(this.model.truncateTitle(MOOC.views.KQ_TITLE_MAX_LENGTH));
                    if (!(/[\w\/]+\/q/.test(path))) {
                        path = path + "/q";
                        MOOC.router.navigate(path, { trigger: false });
                    }
                    this.setEventForNavigation("#kq-previous", unit, this.model, false);
                    this.setEventForNavigation("#kq-next", unit, this.model, true);

                    if (_.isUndefined(view)) {
                        view = new MOOC.views.Question({
                            model: question,
                            el: $("#kq-video")[0]
                        });
                        MOOC.views.questionViews[question.get("id")] = view;
                    }
                    // We need to destroy the iframe with a callback because the
                    // question view needs to read the width/height of the video
                    view.render(_.bind(this.destroyVideo, this));
                }, this));

                async.series(toExecute);
            }
        }

        return this;
    },

    loadSolution: function () {
        "use strict";
        var toExecute = [];

        toExecute.push(_.bind(this.repeatedlyCheckIfPlayer, this));
        toExecute.push(_.bind(function (callback) {
            _.bind(this.destroyVideo, this)();
            callback();
        }, this));

        if (!this.model.has("questionInstance")) {
            toExecute.push(async.apply(this.setupListernerFor, this.model, "questionInstance"));
        }

        toExecute.push(_.bind(function (callback) {
            var height = this.getVideoHeight(),
                unit = MOOC.models.course.getByKQ(this.model),
                html = "";

            if (!_.isNull(this.model.get("questionInstance").get("solution"))) {
                html = '<iframe id="ytplayer" width="100%" height="' + height + 'px" ';
                html += 'src="//www.youtube.com/embed/' + this.model.get("questionInstance").get("solution");
                html += '?rel=0&origin=' + MOOC.host + '" frameborder="0" allowfullscreen></iframe>';
            } else {
                MOOC.alerts.show(MOOC.alerts.INFO, MOOC.trans.api.solutionNotReadyTitle, MOOC.trans.api.solutionNotReady);
            }

            $("#kq-video").html(html);
            $("#kq-video").css("height", "auto");
            $("#kq-q-buttons").addClass("hide");
            $("#kq-next-container").addClass("offset4");
            $("#kq-title").html(this.model.truncateTitle(MOOC.views.KQ_TITLE_MAX_LENGTH));

            this.setEventForNavigation("#kq-previous", unit, this.model, false);
            this.setEventForNavigation("#kq-next", unit, this.model, true);

            callback();
        }, this));

        async.series(toExecute);

        return this;
    },

    destroyVideo: function () {
        "use strict";
        var node = $("#kq-video"),
            height = node.css("height");

        if (!_.isUndefined(height)) {
            node.css("height", height);
        }
        node.empty();
        this.player = null;
    }
});

MOOC.views.kqViews = {};

MOOC.views.Question = Backbone.View.extend({
    render: function (destroyPlayer) {
        "use strict";
        var kqPath = window.location.hash.substring(1, window.location.hash.length - 2), // Remove trailing /q
            answer = this.model.get('answer'),
            html;

        if (this.model.get("use_last_frame")) {
            html = '<img src="' + this.model.get("lastFrame") + '" ' +
                'alt="' + this.model.get("title") +
                '" style="width: 620px; height: 372px;" />';
        } else {
            html = "<div class='white' style='width: 620px; height: 372px;'></div>";
        }
        destroyPlayer();
        this.$el.html(html);
        this.$el.css("height", "auto");

        $("#kq-q-buttons").removeClass("hide");

        if (this.model.isActive()) {
            $("#kq-q-submit").attr("disabled", false);
        } else {
            $("#kq-q-submit").attr("disabled", "disabled");
        }

        $("#kq-q-showkq")
            .unbind('click.QuestionView')
            .bind('click.QuestionView', function () {
                MOOC.router.navigate(kqPath, { trigger: true });
            });
        $("#kq-q-submit")
            .unbind('click.QuestionView')
            .bind('click.QuestionView', _.bind(function () {
                this.submitAnswer();
            }, this));
        $("#kq-next-container").removeClass("offset4");

        this.model.get("optionList").each(function (opt) {
            var view = MOOC.views.optionViews[opt.get("id")], reply = null;
            if (_.isUndefined(view)) {
                reply = answer.getReply(opt.get('id'));
                view = new MOOC.views.Option({
                    model: opt,
                    reply: reply,
                    el: $("#kq-video")[0]
                });
                MOOC.views.optionViews[opt.get("id")] = view;
            }
            view.render();
        });

        return this;
    },

    submitAnswer: function () {
        "use strict";
        var self = this,
            answer = this.model.get('answer'),
            replies,
            fetch_solutions;

        replies = this.model.get("optionList").map(function (opt) {
            var view = MOOC.views.optionViews[opt.get("id")],
                input = view.$el.find("input#option" + opt.get("id")),
                type = input.attr("type"),
                value;

            if (type === "text") {
                value = input.val();
            } else {
                value = !_.isUndefined(input.attr("checked"));
            }

            return new MOOC.models.Reply({
                option: view.model.get("id"),
                value: value
            });
        });
        if (replies.length > 0) {
            answer.set('replyList', new MOOC.models.ReplyList(replies));
            answer.set('date', new Date());

            fetch_solutions = self.model.get("optionList").any(function (option) {
                return _.isNull(option.get("solution"));
            });

            MOOC.ajax.sendAnswer(answer, this.model.get('id'), function (data, textStatus, jqXHR) {
                if (jqXHR.status === 201 || jqXHR.status === 204) {
                    answer.set('id', self.model.get('id'));
                    self.model.set('answer', answer);

                    self.loadSolution(fetch_solutions);
                }
            });
        }
    },

    loadSolution: function (fetch_solutions) {
        "use strict";
        // Set the solution for each option.
        // As there is an answer already, the options will have the solution included
        var self = this, answer = this.model.get('answer'),
            load_reply = function (oid, solution) {
                var view = MOOC.views.optionViews[oid],
                    reply = answer.getReply(oid);
                view.setReply(reply);
                self.model.get('optionList').get(oid).set('solution', solution);
                view.render();
            },
            show_result_msg = function () {
                var correct = self.model.isCorrect();
                if (_.isUndefined(correct)) {
                    MOOC.alerts.show(MOOC.alerts.INFO,
                                     MOOC.trans.classroom.answersSent,
                                     MOOC.trans.classroom.answersUnknown);
                } else if (correct) {
                    MOOC.alerts.show(MOOC.alerts.SUCCESS,
                                     MOOC.trans.classroom.answersSent,
                                     MOOC.trans.classroom.answersCorrect);
                } else {
                    MOOC.alerts.show(MOOC.alerts.ERROR,
                                     MOOC.trans.classroom.answersSent,
                                     MOOC.trans.classroom.answersIncorrect);
                }
            };


        if (fetch_solutions) {
            MOOC.ajax.getOptionsByQuestion(this.model.get("id"), function (data, textStatus, jqXHR) {
                _.each(data.objects, function (opt) {
                    load_reply(opt.id, opt.solution);
                });
                show_result_msg();
            });
        } else {
            this.model.get('optionList').each(function (opt_obj) {
                load_reply(opt_obj.get('id'), opt_obj.get('solution'));
                show_result_msg();
            });
        }
    }
});

MOOC.views.questionViews = {};

MOOC.views.Option = Backbone.View.extend({
    MIN_TEXT_HEIGHT: 14,

    types: {
        l: "textarea",
        t: "text",
        c: "checkbox",
        r: "radio"
    },

    initialize: function () {
        "use strict";
        this.reply = this.options.reply;
    },

    setReply: function (reply) {
        "use strict";
        this.reply = reply;
    },

    render: function () {
        "use strict";
        var image = this.$el.find("img"),
            optiontype = this.model.get('optiontype'),
            solution = this.model.get('solution'),
            width = "auto;",
            height = "auto;",
            tag = "input",
            content = "",
            attributes = {
                type: this.types[optiontype],
                id: 'option' + this.model.get('id')
            },
            widthScale = 540 / 620,
            heightScale = 324 / 372;

        if (optiontype === 't') {
            width = Math.floor(this.model.get('width') / widthScale) + 'px;';
            height = Math.floor(this.model.get('height') / heightScale);
            if (height < this.MIN_TEXT_HEIGHT) {
                height = this.MIN_TEXT_HEIGHT;
            }
            height = height + 'px;';
        }

        attributes.style = [
            'top: ' + Math.floor(this.model.get('y') / heightScale) + 'px;',
            'left: ' + Math.floor(this.model.get('x') / widthScale) + 'px;'
        ];
        if (optiontype === 'l') {
            attributes.cols = this.model.get("width");
            attributes.rows = this.model.get("height");
            attributes.disabled = "disabled";
            attributes["class"] = "text";
            tag = attributes.type;
            delete attributes.type;
            content = this.model.get("text");
            attributes.style.push('resize: none;');
            attributes.style.push('cursor: default;');
        } else {
            attributes.style.push('width: ' + width + 'px;');
            attributes.style.push('height: ' + height + 'px;');
        }
        attributes.style = attributes.style.join(' ');
        if (optiontype === 'r') {
            attributes.name = 'radio';
        }

        if (this.reply && this.reply.get('option') === this.model.get('id') && optiontype !== 'l') {
            if (optiontype === 't') {
                attributes.value = this.reply.get('value');
                if (!(_.isUndefined(solution) || _.isNull(solution))) {
                    attributes['class'] = this.model.isCorrect(this.reply) ? 'correct' : 'incorrect';
                }
            } else {
                if (this.reply.get('value')) {
                    attributes.checked = 'checked';
                }
                if (!(_.isUndefined(solution) || _.isNull(solution))) {
                    attributes['class'] = this.model.isCorrect(this.reply) ? 'correct' : 'incorrect';
                }
            }
        }
        this.$el.find("#" + attributes.id).remove();
        this.$el.append(this.make(tag, attributes, content));

        return this;
    }
});

MOOC.views.optionViews = {};

MOOC.views.Attachment = Backbone.View.extend({
    render: function () {
        "use strict";
        var html = "<li><a href='" + this.model.get("url") + "' target='_blank'>",
            parts = this.model.get("url").split('/');
        html += parts[parts.length - 1];
        html += "</a></li>";
        this.$el.append(html);
        return this;
    }
});
