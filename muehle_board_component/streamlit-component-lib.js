(function () {
  function makeEventTarget() {
    if (typeof EventTarget !== "undefined") return new EventTarget();
    const listeners = new Map();
    return {
      addEventListener: (type, cb) => {
        const arr = listeners.get(type) || [];
        arr.push(cb);
        listeners.set(type, arr);
      },
      removeEventListener: (type, cb) => {
        const arr = listeners.get(type) || [];
        listeners.set(type, arr.filter((x) => x !== cb));
      },
      dispatchEvent: (evt) => {
        const arr = listeners.get(evt.type) || [];
        arr.forEach((cb) => cb(evt));
        return true;
      },
    };
  }

  const ComponentMessageType = {
    COMPONENT_READY: "streamlit:componentReady",
    SET_COMPONENT_VALUE: "streamlit:setComponentValue",
    SET_FRAME_HEIGHT: "streamlit:setFrameHeight",
  };

  const Streamlit = {
    API_VERSION: 1,
    RENDER_EVENT: "streamlit:render",
    events: makeEventTarget(),
    _registered: false,
    _lastFrameHeight: undefined,

    setComponentReady: function () {
      if (!Streamlit._registered) {
        window.addEventListener("message", Streamlit._onMessageEvent);
        Streamlit._registered = true;
      }
      Streamlit._sendBackMsg(ComponentMessageType.COMPONENT_READY, {
        apiVersion: Streamlit.API_VERSION,
      });
    },

    setFrameHeight: function (height) {
      if (height === undefined) height = document.body.scrollHeight;
      if (height === Streamlit._lastFrameHeight) return;
      Streamlit._lastFrameHeight = height;
      Streamlit._sendBackMsg(ComponentMessageType.SET_FRAME_HEIGHT, { height });
    },

    setComponentValue: function (value) {
      Streamlit._sendBackMsg(ComponentMessageType.SET_COMPONENT_VALUE, {
        value,
        dataType: "json",
      });
    },

    _sendBackMsg: function (type, data) {
      window.parent.postMessage(
        Object.assign({ isStreamlitMessage: true, type }, data),
        "*"
      );
    },

    _onMessageEvent: function (event) {
      const data = event.data || {};
      if (data.type !== Streamlit.RENDER_EVENT) return;

      const detail = {
        disabled: Boolean(data.disabled),
        args: data.args || {},
        theme: data.theme,
      };

      let evt;
      try {
        evt = new CustomEvent(Streamlit.RENDER_EVENT, { detail });
      } catch {
        evt = document.createEvent("CustomEvent");
        evt.initCustomEvent(Streamlit.RENDER_EVENT, false, false, detail);
      }
      Streamlit.events.dispatchEvent(evt);
    },
  };

  window.Streamlit = Streamlit;
})();