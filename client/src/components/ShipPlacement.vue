<template>
  <div>
    <div v-if="board" class="board">
      <table class="board-table">
        <tbody>
          <tr v-for="(_, row) in rows" :key="row">
            <td v-for="(_, col) in cols" :key="col" class="board-cell">
              <div
                class="board-cell-content"
                @drop="onDrop($event, row, col)"
                @dragenter.prevent
                @dragover.prevent
              >
                &nbsp;
                <div
                  v-if="board[row][col] != -1"
                  :class="[
                    getShipClassName(
                      ships[board[row][col]]['length'],
                      ships[board[row][col]]['orientation']
                    ),
                  ]"
                  draggable="true"
                  @dragstart="onDragStart($event, board[row][col])"
                  @click="rotate($event, board[row][col])"
                ></div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!-- <div class="clues">
      * double click to rotate * drag and drop to move
    </div> -->
    <div>
      <button class="btn" @click="randomizeShips">randomize</button>
    </div>
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
import {
  getNewOrientation,
  getOffset,
  getTempShipsAndNewShip,
  isPlacementPossible,
  placeShips,
  zeros,
} from "../helpers";
var _ = require("lodash");

export default {
  props: {
    rows: Number,
    cols: Number,
  },
  computed: {
    ...mapState(["ships"]),
    board() {
      let board = zeros(this.rows, this.cols, -1);
      for (let i = 0; i < this.ships.length; i++) {
        board[this.ships[i].x][this.ships[i].y] = i;
      }
      return board;
    },
  },
  methods: {
    ...mapActions(["randomizeShips"]),
    getShipClassName(length, orientation) {
      return `ship-${orientation}-${length}`;
    },
    onDragStart(event, shipIndex) {
      event.dataTransfer.dropEffect = "move";
      event.dataTransfer.effectAllowed = "move";

      // let size = event.path[2].clientWidth; // + clientTop / + clientLeft
      // let offsetRow = Math.floor(event.offsetY / size);
      // let offsetCol = Math.floor(event.offsetX / size);
      let [offsetRow, offsetCol] = getOffset(event);

      event.dataTransfer.setData("shipIndex", shipIndex);
      event.dataTransfer.setData("offsetRow", offsetRow);
      event.dataTransfer.setData("offsetCol", offsetCol);
    },
    onDrop(event, x, y) {
      let shipIndex = event.dataTransfer.getData("shipIndex");
      let offsetRow = parseInt(event.dataTransfer.getData("offsetRow"));
      let offsetCol = parseInt(event.dataTransfer.getData("offsetCol"));

      let newX = x - offsetRow;
      let newY = y - offsetCol;

      let [tempShips, ship] = getTempShipsAndNewShip(this.ships, shipIndex);
      ship.x = newX;
      ship.y = newY;

      let currentBoard = placeShips(this.rows, this.cols, tempShips);
      if (isPlacementPossible(currentBoard, ship, this.rows, this.cols)) {
        this.$set(this.ships, shipIndex, ship);
      }
    },
    rotate(event, shipIndex) {
      let [offsetRow, offsetCol] = getOffset(event);
      let [tempShips, ship] = getTempShipsAndNewShip(this.ships, shipIndex);

      ship.rows = this.ships[shipIndex].cols;
      ship.cols = this.ships[shipIndex].rows;

      let clickedX = this.ships[shipIndex].x + offsetRow;
      let clickedY = this.ships[shipIndex].y + offsetCol;

      ship.x = clickedX - offsetCol;
      ship.y = clickedY - offsetRow;
      ship.orientation = getNewOrientation(this.ships[shipIndex].orientation);

      let currentBoard = placeShips(this.rows, this.cols, tempShips);
      if (isPlacementPossible(currentBoard, ship, this.rows, this.cols)) {
        this.$set(this.ships, shipIndex, ship);
      }
    },
  },
};
</script>
