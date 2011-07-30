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
