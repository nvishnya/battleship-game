<template>
  <div
    v-if="shots"
    :class="[
      yours ? 'you' : 'opponent',
      'board',
      waiting ||
      isOver ||
      opponentLeft ||
      (!yours && !yourTurn) ||
      (yours && yourTurn)
        ? 'board-disabled'
        : ''
    ]"
  >
    <div class="board-owner" v-if="yours">YOUR BOARD</div>
    <div class="board-owner" v-else>OPPONENT'S BOARD</div>
    <table class="board-table">
      <tbody>
        <tr v-for="(_, x) in rows" :key="x">
          <td
            v-for="(_, y) in cols"
            :key="y"
            class="board-cell"
            :class="{
              'board-cell-hit': shots[x][y] == 2,
              'board-cell-ship-part': board[x][y] != 0
            }"
          >
            <div
              @click="
                if (!waiting && !yours && shots[x][y] == 0) {
                  makeMove({ x: x, y: y });
                }
              "
              class="board-cell-content"
            >
              &nbsp;
              <div
                :class="{
                  'ship-part': board[x][y] != 0 && shots[x][y] != 2,
                  'shot-miss': shots[x][y] == 1,
                  'shot-hit': shots[x][y] == 2
                }"
              >
                &nbsp;
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
export default {
  props: {
    rows: Number,
    cols: Number,
    board: Array,
    shots: Array,
    yours: Boolean,

    waiting: Boolean
  },
  computed: {
    ...mapState(["isOver", "opponentLeft", "yourTurn"])
  },
  methods: {
    ...mapActions(["makeMove"])
  }
};
</script>
