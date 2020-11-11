import Vue from "vue";
import Vuex from "vuex";
import axios from "axios";
import router from "@/router";
import { getSocketUrl } from "@/helpers.js";
import { codePointAt } from "core-js/fn/string";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    socket: null
  },
  mutations: {
    closeSocket(state) {
      state.socket.close();
    },
    changeSocketURL(state, gameId) {
      let url = getSocketUrl(gameId);
      state.socket = new WebSocket(url);
    }
  },
  actions: {
    initSocket({ commit }) {
      
      let gameId = router.currentRoute.params.id;
      commit("changeSocketURL", gameId);
    },

    async createGameWithFriend({ commit }, payload) {
      const response = await axios.post("new-game/", {
        rows: payload.rows,
        cols: payload.cols
      });
      let gameId = response.data.game_id;
      router.push({ name: "Game", params: { id: gameId } });
      commit("closeSocket")
      commit("changeSocketURL", gameId);

      // send start command to ws ?
    },

    startGame() {

    },
    makeMove() {

    }

  },
  modules: {}
});
