<template>
  <div>
    <div v-if="board" class="board">
      <table class="board-table board-table-placement">
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
    <div>
      <button class="blue-button" @click="randomizeShips">randomize</button>
    </div>
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
import {
  getClicked,
  getDifference,
  getNewOrientation,
  getOffset,
  getTempShipsAndNewShip,
  isPlacementPossible,
  placeShips,
  rotateMatrix,
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
      if (this.ships[shipIndex].length == 1) {
        return;
      }

      let [offsetRow, offsetCol] = getOffset(event);
      let [tempShips, ship] = getTempShipsAndNewShip(this.ships, shipIndex);

      let clickedX = getClicked(this.ships[shipIndex].x, offsetRow);
      let clickedY = getClicked(this.ships[shipIndex].y, offsetCol);

      let diffRow = getDifference(ship.rows, offsetRow);
      let diffCol = getDifference(ship.cols, offsetCol);
      let maxDiff = _.max([diffRow, diffCol]);

      let size = maxDiff * 2 + 1;

      let centerTemp = Math.floor(size / 2);
      let x = centerTemp - offsetRow;
      let y = centerTemp - offsetCol;

      let shipMatrix = zeros(size, size, 0);
      for (let i = x; i < x + ship.rows; i++) {
        for (let j = y; j < y + ship.cols; j++) {
          shipMatrix[i][j] = 1;
        }
      }

      let initX = clickedX - maxDiff;
      let initY = clickedY - maxDiff;

      let newX, newY;
      let rotated = rotateMatrix(shipMatrix);
      for (let i = 0; i < size; i++) {
        for (let j = 0; j < size; j++) {
          if (rotated[i][j] == 1) {
            [newX, newY] = [initX + i, initY + j];
            [i, j] = [size, size];
          }
        }
      }

      ship.rows = this.ships[shipIndex].cols;
      ship.cols = this.ships[shipIndex].rows;
      ship.x = newX;
      ship.y = newY;
      ship.orientation = getNewOrientation(this.ships[shipIndex].orientation);

      let currentBoard = placeShips(this.rows, this.cols, tempShips);
      if (isPlacementPossible(currentBoard, ship, this.rows, this.cols)) {
        this.$set(this.ships, shipIndex, ship);
      }
    },
  },
};
</script>
