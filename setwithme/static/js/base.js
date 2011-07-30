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
        $(this).toggleClass('active');
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
    }
};
