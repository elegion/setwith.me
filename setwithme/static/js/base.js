SetWithMe = {};

$.extend(SetWithMe, {
    REQUEST_INTERVAL: 1000
});

/**
 *
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

    _onSuccess: function(data) {
        window.console && console.debug('SUCCESS:', data);
        this._timer = setTimeout(this._request.bind(this), SetWithMe.REQUEST_INTERVAL);
    },

    _onError: function(jqXHR, textStatus) {
        window.console && console.error('Error:', textStatus);
    },

    start: function() {
        this._request();
    },

    stop: function() {
        if (this._timer) {
            clearTimeout(this._timer);
        }
    }
};

SetWithMe.init = function() {
    this.poller = new SetWithMe.Poller('/stub/');
    this.poller.start();
};

SetWithMe.uninit = function() {
    this.poller.stop();
};

SetWithMe.init();
