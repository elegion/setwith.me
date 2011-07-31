SetWithMe = {};

$.extend(SetWithMe, {
    REQUEST_INTERVAL: 1000,
    SET_CHOOSE_TIME: 10
});

SetWithMe.initFacebookLogin = function() {
    var $login_form = $('#js_facebook_login'),
    $login_button = $login_form.find('.js_submit');
    $login_button.click(function(event) {
        event.preventDefault();
        FB.login(function(response) {
            if (response && response.status == 'connected') {
                window.location.replace('/login/facebook/');
            }
        });
    });
};

/**
 * @constructor
 * @param {String} u
 * @param {String} m
 */
SetWithMe.Poller = function(u, m) {
    if (m) {
        this._method = m;
    }
    this._url = u;
};

SetWithMe.Poller.prototype = {
    /** @type String */
    _method: 'GET',
    /** @type Number */
    _timer: 0,
    /** @type String */
    _url: '',

    _request: function() {
        $.ajax({
            dataType: 'json',
            url: this._url,
            success: this._onSuccess.bind(this),
            error: this._onError.bind(this)
        })
    },

    /**
     *
     * @param {Object} data
     */
    _onSuccess: function(data) {
        this._timer = setTimeout(this._request.bind(this), SetWithMe.REQUEST_INTERVAL);
        try {
            this.onSuccess(data);
        } catch (e) {
            console && console.error(e);
        }
    },

    onSuccess: function() {},

    /**
     *
     * @param {} jqXHR
     * @param {String} textStatus
     */
    _onError: function(jqXHR, textStatus) {
        console && console.error(textStatus);
        this._timer = setTimeout(this._request.bind(this), SetWithMe.REQUEST_INTERVAL);
        try {
            this.onError();
        } catch (e) {
            console && console.error(e);
        }
    },

    onError: function() {},

    start: function() {
        this._request();
    },

    stop: function() {
        if (this._timer) {
            clearTimeout(this._timer);
        }
    }
};

SetWithMe.searchGame = function() {
    var poller = new SetWithMe.Poller('/game/create/');
    poller.onSuccess = function(data) {
        if (data.status == 302) {
            window.location.replace(data.url);
            poller.stop();
        }
        if (data.opponents) {
            var $players_list = $('#js_opponents'),
            opponents = [];
            for (var i = 0; i < data.opponents.length; i++) {
                var op = data.opponents[i];
                var pic = op.pic || '/static/images/nophoto.png';
                var op_rendered = '<li class="player" id="p' + op.username + '">'+
                        '<div class="photo"><div><img src="' + pic + '"></div></div>'+
                        '<div class="info">'+
                        '<a href="#" class="name">'+ op.name +'</a>'+
                        '</div></li>';
                opponents.push(op_rendered);
            }
            $players_list.html(opponents.join(''));
        }
        if (data.timeout) {
            $('#countdown').show();
            $('#countdown .timer').text(data.timeout);
        }
    };
    poller.start();
};

SetWithMe.getCookie = function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};


SetWithMe.Game = {
    statuses: {
        'NORMAL': 'normal',
        'SET_CHOOSE': 'set_choose',
        'PENALTY': 'penalty',
        'GAME_END': 'gameend',
        SET_ANOTHER_USER: 'set_another_user'
    },
    _status: null,
    _statusChangedAt: null,

    /** @type Array */
    _cards: null,
    /** @type Boolean */
    _markingSet: false,
    /** @type String */
    _id: '',
    /** @type SetWithMe.Poller */
    _poller: null,

    _timeLeft: -1,

    _CSRFToken: '',

    _user: null,

    _users: null,

    _changeStatus: function (newStatus) {
        if (newStatus == this._status) {
            return;
        }
        this._status = newStatus;
        this._statusChangedAt = new Date();

        if (newStatus == this.statuses.NORMAL) {
            //clean up all
            this._setButtonLabel.text('Set!');
            this._setButton.removeClass('disabled');
            this._markingSet = false;
            this._countDownLabel.text('');
            this._cardsContainer.removeClass('active');
        }

        if (newStatus == this.statuses.PENALTY) {
            this._setButton.addClass('disabled');
            this._stopCountDown();
            this._setButtonLabel.text('Blocked. Waiting for other players move.');
            this._cardsContainer.removeClass('active');
            $('.card', this._cardsContainer).removeClass('active');
        }

        if (newStatus == this.statuses.GAME_END) {
            $('#p' + this._leader).clone().appendTo($('#js_user_place'));
            this.uninit();
            $('.winner_plate').show();
        }

        if (newStatus == this.statuses.SET_ANOTHER_USER) {
            this._setButtonLabel.text('Another user choosing the set...');
            this._setButton.addClass('disabled');
        }
    },

    _updateStatus: function() {

    },


    /**
     * @param {String} id
     */
    init: function(id) {
        this.$cards = $('#js_cards');
        this.$users = $('#js_players');
        this._cardsContainer = $('#js_cards');
        this._setButton = $('#js_set_button');
        this._setButtonLabel = $('#js_set_button_label');
        this._countDownLabel = $('#js_countdown');
        this._cardsLeftLabel = $('#js_cards_left');
        this._CSRFToken = SetWithMe.getCookie('csrftoken');
        this._id = id;
        this._poller = new SetWithMe.Poller('/game/get_status/' + this._id);
        this._poller.onSuccess = this._onStatusReceived.bind(this);
        this._poller.onError = this._poller.onSuccess.bind(this);
        this._poller.start();

        this._status = this.statuses.NORMAL;
        this._statusInterval = setInterval(SetWithMe.Game._updateStatus, 1000);
    },

    uninit: function() {
        if (this._poller) {
            this._poller.stop();
        }
    },

    _onCountDown: function() {
        if (this._timeLeft < 0) {
            this._timeLeft = SetWithMe.SET_CHOOSE_TIME;
            this._countDownLabel.text(this._timeLeft);
            this._cardsContainer.addClass('active');
        } else if (this._timeLeft === 0) {
            this._changeStatus(this.statuses.PENALTY);
        } else {
            this._countDownLabel.text(--this._timeLeft);
        }
    },

    _startCountDown: function() {
        this._countDown_timer = setInterval(this._onCountDown.bind(this), 1000);
    },

    _stopCountDown: function() {
        if (this._countDown_timer) {
            clearInterval(this._countDown_timer);
            this._markingSet = false;
            this._timeLeft = -1;
            this._countDownLabel.text('');
        }
    },

    markSet: function(event) {
        event.preventDefault();
        if (this._setButton.hasClass('disabled') || this._markingSet) {
            return;
        }
        this._markingSet = true;
        this._setButton.addClass('disabled');
        this._setButtonLabel.text('Show us set bellow...');
        this._startCountDown();
        this._sendPutSet();
    },

    _checkSet: function($cards) {
        var valid = true,
            setIds = [],
            attrs = [[],[],[],[]];
        $cards.each(function(i, elem) {
            var className = elem.className.replace(/\s?(card|active)\s?/gi, ''),
                props = className.split(' ');
            setIds.push(elem.id);
            for (var i=0; i<4; i++) {
                attrs[i].push(props[i]);
            }
        });
        for(var i=0; i<attrs.length && valid; i++) {
            $.unique(attrs[i]);
            if (attrs[i].length == 2) {
                valid = false;
            }
        }
        if (valid) {
            return setIds.join(',');
        }
        return false;
    },

    _onPutSet: function(data) {
        if (data.success === false) {
            this._stopCountDown();
            this._changeStatus(this.statuses.SET_ANOTHER_USER);
        }
    },

    _sendPutSet: function() {
        $.ajax({
            headers: {
                'X-CSRFToken': this._CSRFToken
            },
            success: this._onPutSet.bind(this),
            url: '/game/put_set_mark/' + this._id,
            type: 'POST'
        })
    },

    _onSendSet: function(data) {
        if (data.success === true) {
            var $activeCards = $('.active', SetWithMe.Game._cardsContainer);
            $activeCards.animate({opacity: '0'}, 1000);
            $activeCards.removeClass('.active');
            this._updateScore(data);
            this._changeStatus(this.statuses.NORMAL);
        }
    },

    _sendSet: function(data) {
        this._stopCountDown();
        $.ajax({
            data: {
                ids: data
            },
            headers: {
                'X-CSRFToken': this._CSRFToken
            },
            success: this._onSendSet.bind(this),
            url: '/game/check_set/' + this._id,
            type: 'POST'
        });
    },

    /**
     * @param {Array} newCards
     * @return {Object}
     */
    _getChangedCards: function(newCards) {
        var i,
            changedCards = {};
        for (i = 0; i < this._cards.length; i++) {
            if (this._cards[i].id !== newCards[i].id) {
                changedCards[i] = newCards[i];
                changedCards[i].oldId = this._cards[i].id;
            }
        }
        if (newCards.length > this._cards.length) {
            for (i = this._cards.length; i < newCards.length; i++) {
                changedCards[i] = newCards[i];
            }
        }
        return changedCards;
    },

    _bindCardEvents: function($card) {
        $card.click(this._onCardClick);
    },

    /**
     * @param {Object} card
     */
    _renderCard: function(card) {
        var $card = $('<li><i><b></b></i></li>');
        $card.attr('id', card.id);
        $card.attr('class', 'card ' + card['class']);
        this._bindCardEvents($card);
        this._cardsContainer.append($card);
    },

    _renderCards: function() {
        this._cardsContainer.html('');
        for (var i = 0; i < this._cards.length; i++) {
            this._renderCard(this._cards[i])
        }
    },

    _renderPlayer: function(player) {
        var pic = player.user_data.pic || '/static/images/nophoto.png';
        return '<li class="player" id="p' + player.user_data.id + '">'+
             '<div class="photo"><div><img src="' + pic + '"></div></div>'+
             '<div class="info">'+
             '<a href="#" class="name">'+ player.user_data.name +'</a><span class="stats">'+
             '<span class="points"><span class="count"></span> points, </span>'+
             '<span class="sets"><span class="count"></span> sets, </span>'+
             '<span class="failures"><span class="count"></span> failures</span>'+
             '</span></div></li>';
    },

    _renderPlayers: function(users) {
        var player = null;
        for (var i = 0; i < users.length; i++) {
            player = users[i];
            var $player = $('#p'+player.user_data.id);
            if (!$player.length) {
                if (player.me) {
                    SetWithMe.Game.$users.prepend($(this._renderPlayer(player)));
                } else {
                    SetWithMe.Game.$users.append($(this._renderPlayer(player)));
                }
                $player = $('#p' + player.user_data.id);
            }
            this._updateScore(player.user_id, player);

            $player[0].className =
                    ['player', player.client_state.toLowerCase(), player.state.toLowerCase()].join(' ')
        }
    },

    _updateScore: function(user_id, data) {
        if (data) {
            var $player = $('#p' + user_id);

            var $p = $player.find('.points .count');
            var $s = $player.find('.sets .count');
            var $f = $player.find('.failures .count');

    //        if ($p.text() != data.score) $p.parent().coolfade();
            $p.text(data.score);

    //        if ($s.text() != data.sets_found) $s.parent().coolfade();
            $s.text(data.sets_found);

    //        if ($f.text() != data.failures) $f.parent().coolfade();
            $f.text(data.failures);
        }
    },

    _onCardClick: function() {
        var setIds,
            $card = $(this),
            $activeCards = $('.active', SetWithMe.Game._cardsContainer);
        if (!SetWithMe.Game._markingSet) {
            return ;
        }
        if ($activeCards.length > 2) {
            return;
        }
        $card.toggleClass('active');
        if ($activeCards.length === 2) {
            $activeCards = $activeCards.add($card);
            if (setIds = SetWithMe.Game._checkSet($activeCards)) {
                SetWithMe.Game._sendSet(setIds);
            } else {
                $activeCards.vibrate();
                $activeCards.removeClass('active');
            }
        }
    },

    /**
     *
     * @param {Object} data
     */
    _onStatusReceived: function(data) {
        if (this._cards) {
            var changed = this._getChangedCards(data.cards);
            if (!$.isEmptyObject(changed)) {
                console.debug(changed);
                for (var key in changed) {
                    if (changed.hasOwnProperty(key)) {
                        var card = changed[key];
                        var $place = this._cardsContainer.find('#' + card.oldId);
                        console.debug(card)
                        if ($place.length) {
                            if ($place.css('opacity') == 0) {
                                $place.animate({opacity: '0'}, 1000);
                            }
                        } else {
                            $place = $('<li style="opacity: 0"><i><b></b></i></li>');
                            this._bindCardEvents($place);
                            this._cardsContainer.append($place);
                        }
                        console.debug($place);
                        $place.attr('class', 'card ' + card['class']);
                        $place.attr('id', card['id']);
                        $place.animate({opacity: '1'}, 1000);
                    }
                }
                this._cards = data.cards;
                //this._renderCards();
                // TODO re-render changed cards
            }
        } else {
            this._cards = data.cards;
            this._renderCards();
        }


        this._users = data.users;
        for (var i=0; i < this._users.length; i++) {
            if (this._users[i].me) {
                this._user = this._users[i];
                break;
            }
        }
        this._renderPlayers(data.users);
        this._leader = data.game.leader;

        this._cardsLeftLabel.text(data.cards_left);

        //status changes
        if (this._user.state == 'SET_PENALTY') {
            this._changeStatus(this.statuses.PENALTY);
        }
        if (this._user.state == 'NORMAL') {
            this._changeStatus(this.statuses.NORMAL);
        }
        if (this._user.state == 'SET_PRESSED') {
            this._changeStatus(this.statuses.SET_CHOOSE);
        }
        if (this._user.state == 'SET_ANOTHER_USER') {
            this._changeStatus(this.statuses.SET_ANOTHER_USER);
        }
        if (data.game.is_finished) {
            this._changeStatus(this.statuses.GAME_END);
        }
    }
};

SetWithMe.attributes =  {
    'count': ['one', 'two', 'three'],
    'symbol': ['oval', 'diamond', 'squiggle'],
    'shading': ['solid', 'open', 'striped'],
    'color': ['red', 'green', 'blue']
};

SetWithMe.generateSet = function() {
    //generates random set
    var result = [[],[],[]];
    var i = 0;
    for (var attr in SetWithMe.attributes) {
        var similar = Math.random() > 0.5;
        var num = Math.ceil(Math.random() * 3) - 1;
        for (var j=0; j<result.length; j++) {
            result[j][i] = similar ? SetWithMe.attributes[attr][num]: SetWithMe.attributes[attr][j];
        }
        i += 1;
    }
    return [result[0].join(' '), result[1].join(' '), result[2].join(' ')];
};

$(function() {
    $('#js_header_cards').click(function() {
       $('#js_header_cards').fadeOut(function() {
       var set = SetWithMe.generateSet();
       for (var i=0; i < $('#js_header_cards .card').length; i++) {
           $('#js_header_cards .card')[i].setAttribute('class', 'mini card ' + set[i]);
       }});
       $('#js_header_cards').fadeIn();
    });

    $('#js_rotate_logo').click(function(){
        $('#js_header_cards').click();
    });

    var $jsSearching = $('#js_searching');
    if ($jsSearching.length) {
        setInterval(function() {
            $jsSearching.fadeOut(1000, function() {
                var set = SetWithMe.generateSet();
                for (var i=0; i < $jsSearching.find('.card').length; i++) {
                    $jsSearching.find('.card')[i].setAttribute('class', 'card ' + set[i]);
                }
                $jsSearching.fadeIn(1500);
            })}, 2000);
    }
    $('.js_chat_message_form').ajaxForm({
        'success': function(data) {
            console.log('message form success');
        }
    });
});

jQuery.fn.vibrate = function (conf) {
    var config = jQuery.extend({
        speed: 30,
        duration: 1000,
        spread: 5
    }, conf);

    return this.each(function () {
        var t = jQuery(this);
        t.addClass('vibrate');

        var vibrate = function () {
            var topPos    = Math.floor(Math.random() * config.spread) - ((config.spread - 1) / 2);
            var leftPos    = Math.floor(Math.random() * config.spread) - ((config.spread - 1) / 2);
            var rotate    = Math.floor(Math.random() * config.spread) - ((config.spread - 1) / 2);

            t.css({
                position:            'relative',
                left:                leftPos + 'px',
                top:                topPos + 'px',
                WebkitTransform:    'rotate(' + rotate + 'deg)'  // cheers to erik@birdy.nu for the rotation-idea
            });
        };

        var doVibration = function () {
            var vibrationInterval = setInterval(vibrate, config.speed);

            var stopVibration = function () {
                clearInterval(vibrationInterval);
                t.css({
                    position:            'static',
                    WebkitTransform:    'rotate(0deg)'
                });
                t.removeClass('vibrate');
            };

            setTimeout(stopVibration, config.duration);
        };

        doVibration();
    });
};

jQuery.fn.coolfade = function() {
    var self = this;
    this.fadeOut(function() {self.fadeIn()});
}
