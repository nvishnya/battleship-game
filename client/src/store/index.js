import Vue from "vue";
import Vuex from "vuex";
import axios from "axios";
import router from "@/router";
import { getSocketUrl, zeros } from "../helpers";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    socket: null,

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
    link: null
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
    saveGameId(state, gameId) {
      if (gameId != undefined) {
        state.savedGameId = gameId;
        state.friendAsOpponent = true;
        state.link = document.URL;
      }
    },
    updateShips(state, ships) {
      state.ships = ships;
    },
    setFriendOpponent(state, friend) {
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
    }
  },
  actions: {
    initSocket({ commit, dispatch }, payload) {
      let gameId = router.currentRoute.params.id;
      if (payload.reloadShips) {
        dispatch("randomizeShips");
      }
      commit("saveGameId", gameId);
      commit("closeSocket");
      commit("changeSocketURL", gameId);
      if (payload != undefined && payload.handler != undefined) {
        commit("addListeners", payload.handler);
      }
    },

    async createGameWithFriendOpponent({ dispatch, commit, state }) {
      if (!state.friendAsOpponent) {
        let gameId = state.savedGameId;
        if (state.savedGameId == null) {
          const response = await axios.post("new-game/", {
            rows: state.rows,
            cols: state.cols
          });
          gameId = response.data.game_id;
          commit("saveGameId", gameId);
        }
        commit("setFriendOpponent", true);
        router.push({ name: "Game", params: { id: gameId } });
        dispatch("initSocket", { reloadShips: false, handler: state.handler });
      }
    },

    createGameWithRandomOpponent({ dispatch, state, commit }) {
      if (state.friendAsOpponent) {
        commit("setFriendOpponent", false);
        router.push({ name: "Game" });
        dispatch("initSocket", { reloadShips: false, handler: state.handler });
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
    startGame({ state, dispatch }) {
      let payload = {
        command: "start",
        ships: state.ships,
        rows: state.rows,
        cols: state.cols
      };
      dispatch("sendSocketMessage", payload);
    },
    updateGame({ commit }, data) {
      // console.log(JSON.parse(data.you.shots))
      commit("updateBoard", data.you.board)
      commit("updateShots", data.you.shots)
      commit("updateOpponent", data.opponent.shots)
      commit("updateCurrentTurn", data.your_turn)
      commit("updateGameStatus", data.is_over)
      commit("updateGameWinner", data.you_won)
    },
    onSocketMessage({ commit, dispatch, state }, data) {
      if (data.type === "waiting-for-opponent") {
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
    },
    makeMove({ dispatch }, payload) {
      payload = {
        command: "move",
        x: payload.x,
        y: payload.y,
      };
      dispatch("sendSocketMessage", payload);
    },
  },
});
