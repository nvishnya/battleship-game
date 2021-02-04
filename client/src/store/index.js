import Vue from "vue";
import Vuex from "vuex";
import axios from "axios";
import router from "@/router";
import { getSocketUrl, zeros } from "../helpers";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    socket: null,
    gameId: null,

    savedGameId: null,
    handler: null,

    ships: [],
    rows: 10,
    cols: 10,

    shipsPlaced: false,
    friendAsOpponent: false,
    gameStarted: false,
    isOver: false,
    youWon: false,

    yourTurn: false,
    board: [],
    shots: [],
    opponent: [],
  },
  mutations: {
    closeSocket(state) {
      if (state.socket != null) {
        state.socket.close();
      }
    },
    saveInitialGameId(state, gameId) {
      state.initialGameId = gameId;
    },
    changeSocketURL(state, gameId) {
      state.socket = new WebSocket(getSocketUrl('ws://127.0.0.1:8000/ws/', gameId));
    },
    addListeners(state, handler) {
      state.handler = handler;
      state.socket.onmessage = handler;
    },
    updateShips(state, ships) {
      state.ships = ships;
    },
    setOpponent(state, friend) {
      state.friendAsOpponent = friend;
    },
    startGame(state) {
      state.gameStarted = true;
    },
    placeShips(state) {
      state.shipsPlaced = true;
    },
    updateBoard(state, board) {
      state.board = JSON.parse(board)
    },
    updateShots(state, shots) {
      state.shots = JSON.parse(shots)
    },
    updateOpponent(state, opponent) {
      state.opponent = JSON.parse(opponent)
    },
    updateCurrentTurn(state, yourTurn) {
      state.yourTurn = yourTurn;
    },
    updateGameStatus(state, isOver) {
      state.isOver = isOver;
    },
    updateGameWinner(state, youWon) {
      state.youWon = youWon;
    },
    updateSocket(state, url) {
      state.socket = new WebSocket(url);
    },
    setGameId(state, id) {
      state.gameId = id;
    },
    closeSocket(state) {
      state.socket.close()
    },

    reset(state) {
      state.gameId = null
      state.ships = []
      state.shipsPlaced = false
      state.friendAsOpponent = false
      state.gameStarted = false
      state.isOver = false
      state.youWon = false
      state.yourTurn = false
      state.board = []
      state.shots = []
      state.opponent = []
    },
  },
  actions: {
    initSocket({ commit, dispatch }, payload) {
      commit('updateSocket', 'ws://127.0.0.1:8000/ws/')
      commit("addListeners", payload.handler);
      dispatch("randomizeShips");
      let gameId = router.currentRoute.params.id;
      gameId = gameId == undefined ? null : gameId;
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
      // else if (data.type == "opponent.left"){
      // }
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
      commit('updateSocket', 'ws://127.0.0.1:8000/ws/')
      commit("addListeners", state.handler);
      dispatch("randomizeShips");
      router.push({ name: "Game" });
    },
  },
});
