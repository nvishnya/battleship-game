import Vue from "vue";
import Vuex from "vuex";
import axios from "axios";
import router from "@/router";
// import { getSocketUrl } from "@/helpers.js";
import { getSocketUrl } from "../helpers";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    socket: null,
    savedGameId: null,
    // gameData: null, ?
  },
  mutations: {
    closeSocket(state) {
      if (state.socket != null) {
        state.socket.close();
      }
    },
    changeSocketURL(state, gameId) {
      state.socket = new WebSocket(getSocketUrl(gameId));
    },
    addListeners(state, handler) {
      state.socket.onmessage = handler;
    },
    saveGameId(state, gameId) {
      state.savedGameId = gameId;
    }
  },
  actions: {
    initSocket({ commit }, payload) {
      let gameId = router.currentRoute.params.id;
      commit("closeSocket");
      commit("changeSocketURL", gameId);
      if (payload != undefined && payload.handler != undefined) {
        commit("addListeners", payload.handler);
      }
    },

    async createGameWithFriendOpponent({ dispatch, commit, state }, payload) {
      let gameId = state.savedGameId;
      if (state.savedGameId == null) {
        const response = await axios.post("new-game/", {
          rows: payload.rows,
          cols: payload.cols
        });
        gameId = response.data.game_id;
        commit("saveGameId", gameId);
      }
      router.push({ name: "Game", params: { id: gameId } });
      dispatch("initSocket");
      // send start command to ws ?
    },

    createGameWithRandomOpponent({ dispatch }) {
      router.push({ name: "Game" });
      dispatch("initSocket");
    },

    sendSocketMessage({ state }, payload) {
      state.socket.send(JSON.stringify(payload));
    }

    // async getRandomlyPositionedShips(_, payload) {
    //   const response = await axios.get(
    //     `random-board/?rows=${payload.rows}&cols=${payload.cols}`
    //   );
    //   return response.data;
    // }
  },
  modules: {}
});
