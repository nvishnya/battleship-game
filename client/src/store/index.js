import Vue from "vue";
import Vuex from "vuex";
import axios from "axios";
import router from "@/router";
import { zeros } from "../helpers";

Vue.use(Vuex);

const initialState = {
  gameId: null,
  ships: [],
  shipsPlaced: false,
  friendAsOpponent: false,
  gameStarted: false,
  isOver: false,
  youWon: false,
  opponentLeft: false,
  yourTurn: false,
  board: [],
  shots: [],
  opponent: []
}

const mutate = (state, prop, value) => {
  state[prop] = value;
}

export default new Vuex.Store({
  state: {
    ...initialState,

    socket: null,
    handler: null,

    rows: 10,
    cols: 10,
  },

  mutations: {
    updateShips: (state, ships) => { mutate(state, "ships", ships) },
    setOpponent: (state, friend) => { mutate(state, "friendAsOpponent", friend) },
    startGame: (state) => { mutate(state, "gameStarted", true) },
    placeShips: (state) => { mutate(state, "shipsPlaced", true) },
    setGameId: (state, id) => { mutate(state, "gameId", id) },
    opponentLeft: (state) => { mutate(state, "opponentLeft", true) },
    updateBoard: (state, board) => { mutate(state, "board", JSON.parse(board)) },
    updateShots: (state, shots) => { mutate(state, "shots", JSON.parse(shots)) },
    updateOpponent: (state, opponent) => { mutate(state, "opponent", JSON.parse(opponent)) },
    updateCurrentTurn: (state, yourTurn) => { mutate(state, "yourTurn", yourTurn) },
    updateGameStatus: (state, isOver) => { mutate(state, "isOver", isOver) },
    updateGameWinner: (state, youWon) => { mutate(state, "youWon", youWon) },
    updateSocket: (state, url) => { mutate(state, "socket", new WebSocket(url)) },
    closeSocket: (state) => { state.socket.close() },
    reset: (state) => { Object.assign(state, initialState) },
    addListeners: (state, handler) => {
      state.handler = handler;
      state.socket.onmessage = handler;
    },
  },

  actions: {
    initSocket({ commit, dispatch }, payload) {
      // commit('updateSocket', 'ws://localhost:8000/ws/')
      commit('updateSocket', 'ws://' + window.location.hostname + ':8000/ws/')
      commit("addListeners", payload.handler);
      dispatch("randomizeShips");
      let gameId = router.currentRoute.params.id;
      gameId = gameId == undefined ? null : gameId;
      let friend = gameId == null ? false : true;
      commit("setOpponent", friend)
      commit("setGameId", gameId)
    },

    async createGameWithFriendOpponent({ dispatch, commit, state }) {
      if (!state.friendAsOpponent) {
        commit("setOpponent", true);
      }
    },

    createGameWithRandomOpponent({ dispatch, state, commit }) {
      if (state.friendAsOpponent) {
        commit("setOpponent", false);
      }
    },

    sendSocketMessage({ state }, payload) {
      state.socket.send(JSON.stringify(payload));
    },

    async randomizeShips({ state, commit }) {
      const response = await axios.get(
        `random-board/?rows=${state.rows}&cols=${state.cols}`
      );
      commit("updateShips", response.data);
    },

    startGame({ state, dispatch, commit }) {
      let payload = {
        command: "start",
        ships: state.ships,
        rows: state.rows,
        cols: state.cols,
        game_id: state.gameId,
        friend_opponent: state.friendAsOpponent
      };
      dispatch("sendSocketMessage", payload);
    },

    updateGame({ commit }, data) {
      commit("updateBoard", data.you.board)
      commit("updateShots", data.you.shots)
      commit("updateOpponent", data.opponent.shots)
      commit("updateCurrentTurn", data.your_turn)
      commit("updateGameStatus", data.is_over)
      commit("updateGameWinner", data.you_won)
    },

    onSocketMessage({ commit, dispatch, state }, data) {
      if (data.type === "waiting-for-opponent") {
        commit("setGameId", data.game_id)
        commit("placeShips");
        commit("updateBoard", data.you.board)
        commit("updateShots", data.you.shots)
        commit("updateOpponent", JSON.stringify(zeros(state.rows, state.cols, 0)))
      }
      else if (data.type === "game.start") {
        commit("placeShips");
        commit("startGame");
        dispatch("updateGame", data.game)
      } else if (data.type === "game.update") {
        dispatch("updateGame", data.game)
      }
      else if (data.type == "opponent.left") {
        commit("opponentLeft")
      }
    },

    makeMove({ dispatch }, payload) {
      payload = {
        command: "move",
        x: payload.x,
        y: payload.y,
      };
      dispatch("sendSocketMessage", payload);
    },

    leaveGame({ state, commit, dispatch }) {
      commit("closeSocket");
      commit("reset");
      commit('updateSocket', 'ws://' + window.location.hostname + ':8000/ws/')
      commit("addListeners", state.handler);
      dispatch("randomizeShips");
      router.push({ name: "Game" });
    },
  },
});
