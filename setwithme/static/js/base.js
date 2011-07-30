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
        this.onSuccess(data);
    },

    onSuccess: function() {},

    /**
     *
     * @param {} jqXHR
     * @param {String} textStatus
     */
    _onError: function(jqXHR, textStatus) {
        this.onError();
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
        this._poller.start();
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
            this._stopCountDown();
            this._setButtonLabel.text('You should choose set faster. Try it next time');
            this._cardsContainer.removeClass('active');
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
        console.debug($cards, $cards.attr('class'));
        var valid = true,
            setIds = [],
            count = [],
            symbol = [],
            shading = [],
            color = [],
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
            if ($.unique(attrs[i]) == 2) {
                valid = false;
            }
        }
        if (valid) {
            return setIds.join(',');
        }
        return false;
    },

    _sendPutSet: function() {
        $.ajax({
            headers: {
                'X-CSRFToken': this._CSRFToken
            },
            url: '/game/put_set_mark/' + this._id,
            type: 'POST'
        })
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
        $card.attr('class', 'card ' + card.class);
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
        return '<li class="player" id="p' + player.user_id + '">'+
             '<div class="photo"><div><img src="/static/images/nophoto.png"></div></div>'+
             '<div class="info">'+
             '<a href="#" class="name">'+ player.user_name +'</a>'+
             '<span class="sets"><span class="count"></span> sets</a>'+
             '</div></li>';
    },

    _renderPlayers: function(users) {
        var player = null;
        for (var i = 0; i < users.length; i++) {
            player = users[i];
            var $player = $('#p'+player.user_id);
            if (!$player.length) {
                SetWithMe.Game.$users.append($(this._renderPlayer(player)));
                $player = $('#p' + player.user_id);
            }
            $player.find('.sets .count').text(player.sets_found);
            $player[0].className = 'player ' + player.client_state.toLowerCase();
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
                SetWithMe.Game._setButtonLabel.text('The cards you are checked is not a set');
                SetWithMe.Game._stopCountDown();
            }
        }
    },

    /**
     *
     * @param {Object} data
     */
    _onStatusReceived: function(data) {
        if (this._cards) {
            if (!$.isEmptyObject(this._getChangedCards(data.cards))) {
                this._cards = data.cards;
                this._renderCards();
                // TODO re-render changed cards
            }
        } else {
            this._cards = data.cards;
            this._renderCards();
        }

        this._renderPlayers(data.users);
        this._users = data.users;

        this._cardsLeftLabel.text(data.cards_left);

        //game ending
        if (data.game.is_finished) {
            $('#p' + data.game.leader).clone().appendTo($('#js_user_place'));
            this.uninit();
            $('.winner_plate').show();
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


