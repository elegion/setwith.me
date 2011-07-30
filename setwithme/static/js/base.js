SetWithMe = {};

$.extend(SetWithMe, {
    REQUEST_INTERVAL: 1000
});

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
        window.console && console.debug('SUCCESS:', data);
        this.onSuccess(data);
        this._timer = setTimeout(this._request.bind(this), SetWithMe.REQUEST_INTERVAL);
    },

    onSuccess: function() {},

    /**
     *
     * @param {} jqXHR
     * @param {String} textStatus
     */
    _onError: function(jqXHR, textStatus) {
        window.console && console.error('Error:', textStatus);
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

SetWithMe.Game = {
    /** @type Array */
    _cards: null,
    /** @type String */
    _id: '',
    /** @type SetWithMe.Poller */
    _poller: null,

    /**
     * @param {String} id
     */
    init: function(id) {
        this.$cards = $('#js_cards');
        this.$users = $('#js_players');
        this.$cardsLeft = $('#js_cards_left');
        this._cardsContainer = $('#js_cards');
        this._id = id;
        this._poller = new SetWithMe.Poller('/game/get_status/' + this._id);
        this._poller.onSuccess = this._onCardsReceived.bind(this);
        this._poller.start();
    },

    uninit: function() {
        if (this._poller) {
            this._poller.stop();
        }
    },

    /**
     * @param {Array} newCards
     * @return {Object}
     */
    _getChangedCards: function(newCards) {
        var i,
            changedCards = {};
        for (i = 0; i < this._cards.length; i++) {
            if (this._cards[i] !== newCards[i]) {
                changedCards[i] = newCards[i];
            }
        }
        return changedCards;
    },

    _bindCardEvents: function($card) {
        $card.click(this._onCardClick);
    },

    /**
     * @param {String} className
     */
    _renderCard: function(className) {
        var $card = $('<li class="card ' + className + '"><i><b></b></i></li>');
        this._bindCardEvents($card);
        this._cardsContainer.append($card);
    },

    _renderCards: function() {
        this._cardsContainer.html('');
        for (var i = 0; i < this._cards.length; i++) {
            this._renderCard(this._cards[i])
        }
    },

    _onCardClick: function() {
        var $card = $(this),
            $activeCards = $('.active', this._cardsContainer);
        if (!$card.hasClass('active') && $activeCards.length >= 3) {
            return;
        }
        $card.toggleClass('active');
    },

    /**
     *
     * @param {Object} data
     */
    _onCardsReceived: function(data) {
        if (this._cards) {
            if (!$.isEmptyObject(this._getChangedCards(data.cards))) {
                this._cards = data.cards;
                // TODO re-render changed cards
            }
        } else {
            this._cards = data.cards;
            this._renderCards();
        }
        var player = null;
        for(var i=0; i<data.users.length; i++) {
            player = data.users[i];
            var $player = $('#p'+player.user_id);
            if (!$player.length) {
                SetWithMe.Game.$users.append($(this._renderPlayer(player)));
                $player = $('#p' + player.user_id);
            }
            $player.find('.sets .count').text(player.sets_found);
            $player[0].class = 'player ' + player.state;
        }        
    },

    _renderPlayer: function(player) {
        return '<li class="player" id="p' + player.user_id + '">'+
             '<div class="photo"><div><img src="/static/images/nophoto.png"></div></div>'+
             '<div class="info">'+
             '<a href="#" class="name">'+ player.user_name +'</a>'+
             '<span class="sets"><span class="count"></span> sets</a>'+
             '</div>'
         '</li>'
    }
};

SetWithMe.attributes =  {
    'count': ['one', 'two', 'three'],
    'symbol': ['oval', 'diamond', 'squiggle'],
    'shading': ['solid', 'open', 'striped'],
    'color': ['red', 'green', 'blue']
}

SetWithMe.generateSet = function() {
    //generates random set
    var result = [[],[],[]];
    var i = 0;
    for(attr in SetWithMe.attributes) {
        var similar = Math.random() > 0.5;
        var num = Math.ceil(Math.random() * 3) - 1;
        for (var j=0; j<result.length; j++) {
            result[j][i] = similar ? SetWithMe.attributes[attr][num]: SetWithMe.attributes[attr][j];
        }
        i += 1;
    }
    return [result[0].join(' '), result[1].join(' '), result[2].join(' ')];
}

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
        var set = SetWithMe.generateSet();
        for (var i=0; i < $jsSearching.find('.card').length; i++) {
            $jsSearching.find('.card')[i].setAttribute('class', 'card ' + set[i]);
        }
    };
    var animate = function() {
        var set = SetWithMe.generateSet($jsSearching.find('.card:last').attr('class').replace('card ', ''));
        for (var i=0; i < set.length; i++) {
            var $newCard = $jsSearching.find('.card:first').clone();
            var first = (i==0)?' first ':'';
            $newCard.attr('class', 'card '  + first + set[i]);
            $jsSearching.append($newCard);
        }
        $jsSearching.find('.card').animate({left: '-=390'}, 5000, function() {
            $jsSearching.find('.card').slice(0,2).remove();
            animate();
        });
    };
//    animate(); doesnt working yet
});
