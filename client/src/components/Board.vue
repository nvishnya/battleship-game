<template>
  <div
    v-if="shots"
    :class="[
      isDisabled ? 'board-disabled' : '',
      yours ? 'you' : 'opponent',
      'board',
    ]"
  >
    <div class="board-owner">
      {{ yours ? "YOUR BOARD" : "OPPONENT'S BOARD" }}
    </div>
    <table class="board-table">
      <tbody>
        <tr v-for="(_, x) in rows" :key="x">
          <td v-for="(_, y) in cols" :key="y"
            :class="[
              {
                'board-cell-hit': shots[x][y] == 2,
                'board-cell-ship-part': board[x][y] != 0,
              },
              'board-cell',
            ]"
          >
            <div
              @click="
                if (isClickable(x, y)) {
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
                  'shot-hit': shots[x][y] == 2,
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

    waiting: Boolean,
  },
  computed: {
    ...mapState(["isOver", "opponentLeft", "yourTurn"]),
    isDisabled() {
      return (
        this.waiting ||
        this.isOver ||
        this.opponentLeft ||
        (!this.yours && !this.yourTurn) ||
        (this.yours && this.yourTurn)
      );
    },
  },
  methods: {
    ...mapActions(["makeMove"]),
    isClickable(x, y) {
      return !this.waiting && !this.yours && this.shots[x][y] == 0;
    },
  },
  methods: {
    ...mapActions(["makeMove"]),
  },
};
</script>
