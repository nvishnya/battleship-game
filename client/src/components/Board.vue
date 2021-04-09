<template>
  <div v-if="shots" :class="[yours ? 'you' : 'opponent', 'board']">
    <div class="board-owner">
      {{ yours ? "YOUR BOARD" : "OPPONENT'S BOARD" }}
    </div>
    <table
      class="board-table"
      :class="[yours ? 'you' : 'opponent', isDisabled ? 'disabled' : 'active']"
    >
      <tbody>
        <tr v-for="(_, x) in rows" :key="x">
          <td v-for="(_, y) in cols" :key="y" class="board-cell">
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
                  'shot-miss': shots[x][y] == 1,
                  'shot-hit': shots[x][y] == 2,
                }"
              ></div>
              <div
                :class="[
                  board[x][y] != -1
                    ? getShipClassName(
                        ships[board[x][y]]['length'],
                        ships[board[x][y]]['orientation']
                      )
                    : '',
                ]"
              ></div>
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
    ships: Array,
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
    isActive() {
      return !(this.waiting || this.isOver || this.opponentLeft);
    },
  },
  methods: {
    ...mapActions(["makeMove"]),
    isClickable(x, y) {
      return !this.waiting && !this.yours && this.shots[x][y] == 0;
    },
    getShipClassName(length, orientation) {
      return `ship-${orientation}-${length}`;
    },
  },
};
</script>
