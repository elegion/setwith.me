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
//    var poller = new SetWithMe.Poller('/game/create/');
//    poller.start();
};

SetWithMe.Game = {}

SetWithMe.Game.init = function(gameId) {
    SetWithMe.Game.gameId = gameId;
    SetWithMe.Game.$cards = $('#js_cards');
    SetWithMe.Game.$users = $('#js_players');
    SetWithMe.Game.$cardsLeft = $('#js_cards_left');

    var poller = new SetWithMe.Poller('/game/status/' + SetWithMe.Game.gameId);
    poller.onSuccess = SetWithMe.Game.render;
    poller.start();
}

SetWithMe.Game.render = function(status) {
    SetWithMe.Game.status = status;

    var card = null;
    SetWithMe.Game.$cards.html("");
    for(var i=0; i<status.cards.length; i++) {
        card = status.cards[i];
        SetWithMe.Game.$cards.append('<li class="card ' + card + '"><i><b></b></i></li>');
    }

    var player = null;
    for(var i=0; i<status.users.length; i++) {
        player = status.users[i];
        var $player = $('#p'+player.user_id);
        if (!$player.length) {
            SetWithMe.Game.$users.append($(SetWithMe.Game.renderPlayer(player)));
            $player = $('#p' + player.user_id);
        }
        $player.find('.sets .count').text(player.sets_found);
        $player[0].class = 'player ' + player.state;
    }
}

SetWithMe.Game.renderPlayer = function(player) {
    return '<li class="player" id="p' + player.user_id + '">'+
         '<div class="photo"><div><img src="/static/images/nophoto.png"></div></div>'+
         '<div class="info">'+
         '<a href="#" class="name">'+ player.user_name +'</a>'+
         '<span class="sets"><span class="count"></span> sets</a>'+
         '</div>'
     '</li>'
}