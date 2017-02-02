/**
 * A pathfinding agent program using a-star with an ALT heuristic.
 * The ALT heuristic uses pre-calculated distances to landmarks 
 * to greatly reduce the search space, with a lower bound function
 * that is closer to the real cost than other commonly known
 * heuristics, relying on the triangular difference principle.
 */

'use strict';

var agent = require('walnut/agent');
var values = require('walnut/core');

var DIRECTIONS = ['North', 'East', 'South', 'West'];
var INVERSE_DIRECTIONS = {
    North: 'South',
    South: 'North',
    East: 'West',
    West: 'East',
    null: null
};


// copied from builtins.js
function hasWall(position, direction, walls) {
    var i, len,
        checkHasWall = false;

    var auxPosition = {x: position.x, y: position.y};

    if (direction === 'South') {
        // A wall to the south in pos (x, y) is a wall to the north in pos (x, y+1)
        auxPosition.y = auxPosition.y + 1;
        direction = 'North';
    } else if (direction === 'East') {
        // A wall to the east in pos (x, y) is a wall to the west in pos (x+1, y)
        auxPosition.x = auxPosition.x + 1;
        direction = 'West';
    }

    if (direction === 'North') {
        walls = walls.north;
    } else if (direction === 'West') {
        walls = walls.west;
    }

    len = walls.length;
    for (i = 0; i < len; i++) {
        if (auxPosition.x === walls[i].x && auxPosition.y === walls[i].y) {
            checkHasWall = true;
            break;
        }
    }
    return checkHasWall;
}

// return the resulting position after a movement
function move(position, direction, gridSize, walls) {
    if (hasWall(position, direction, walls)) {
        // hit a wall, stay there
        return position;
    }

    if ((direction === "North" && position.y === 0) ||
        (direction === "South" && position.y === gridSize[1] - 1) ||
        (direction === "West" && position.x === 0) ||
        (direction === "East" && position.x === gridSize[0] - 1)) {
        // no more board, stay there
        return position;
    }
        
    // can move, do it
    if (direction === "North") {
        return new values.Point({x: position.x, y: position.y - 1});
    } else if (direction === "South") {
        return new values.Point({x: position.x, y: position.y + 1});
    } else if (direction === "West") {
        return new values.Point({x: position.x - 1, y: position.y});
    } else if (direction === "East") {
        return new values.Point({x: position.x + 1, y: position.y});
    }
}


// create a 2 dimensional array
function createTable(gridSize, initialValue) {
    var x, y, table = [];

    for (x = 0; x < gridSize[0]; x++) {
        table.push([]);

        for (y = 0; y < gridSize[1]; y++) {
            table[x].push(initialValue); 
        }
    }

    return table;
}


// estimation from a position to the flag, using a combination of landmark 
// distances and manhattan distances
function heuristic(positionA, positionB, landmarks) {
    var highestPossibleDistance, i, landmark, landmarkToA, landmarkToB, landmarkBound;

    // start with manhattan
    highestPossibleDistance = Math.abs(positionA.x - positionB.x) + Math.abs(positionA.y - positionB.y);

    // but make it higher with landmarks info
    for (i = 0; i < landmarks.length; i++) {
        landmark = landmarks[i];
        landmarkToA = landmark.costs[positionA.x][positionA.y];
        landmarkToB = landmark.costs[positionB.x][positionB.y];
        landmarkBound = Math.abs(landmarkToA - landmarkToB);

        if (landmarkBound > highestPossibleDistance) {
            highestPossibleDistance = landmarkBound;
        }
    }

    return highestPossibleDistance;
}

// get the list of positions and actions from the initial to the node
function getPath(node) {
    var actions = [], 
        currentNode = node;

    while (currentNode !== null) {
        actions.unshift({
            action: currentNode.action, 
            position: currentNode.position,
            cost: currentNode.cost
        });
        currentNode = currentNode.parentNode;
    }

    return actions;
}

// path finding to the flag
function aStarPath(initialPosition, goalPosition, gridSize, walls, landmarks) {
    var fringe = [],
        searchTree = [],
        nodesGrid = createTable(gridSize, null),
        solutionPath = null,
        step, currentNode, newNode, otherNode, i, j, direction, added;

    // sarchTree will contain the list of nodes used in the search, with their 
    // relations and metadata
    // searchGrid will contain the same info, but indexed as a 2 dimentional 
    // array, to be able to lookup nodes by their position

    // add a new node to the fringe
    function addNode(parentNode, action, position, cost, step) {
        if (nodesGrid[position.x][position.y] !== null) {
            return; // already visited
        }

        newNode = {
            parentNode: parentNode,
            action: action,
            position: position, 
            cost: cost,
            heuristic: heuristic(position, goalPosition, landmarks),

            // for metadata:
            parentPosition: null,  // where did it come from?
            cameFrom: INVERSE_DIRECTIONS[action],  // from which direction did it come
            fringeStep: step,  // step in which this node was added to the fringe
            visitedStep: null  // step in which this node was visited
        };
        newNode.g = newNode.cost + newNode.heuristic;

        // for metadata:
        if (parentNode !== null) {
            newNode.parentPosition = parentNode.position;
        }

        // add the node to the fringe, but preserving order
        added = false;
        for (j = 0; j < fringe.length && !added; j++) {
            otherNode = fringe[j];
            if (otherNode.g < newNode.g) {
                fringe.splice(j, 0, newNode);
                added = true;
            }
        }
        if (!added) {
            fringe.push(newNode);
        }

        // store the node in the metadata structures
        searchTree.push(newNode);
        nodesGrid[position.x][position.y] = newNode;
    }

    // check if a node is in the goal position
    function isGoal(node) {
        return node.position.x === goalPosition.x && node.position.y === goalPosition.y;
    }

    // root of the search tree
    addNode(null, null, initialPosition, 0, 0);
 
    // search loop
    step = -1;
    while (fringe.length > 0) {    
        step += 1;
        currentNode = fringe.pop();

        // for metadata:
        currentNode.visitedStep = step;

        if (isGoal(currentNode)) {
            // we arrived to the solution, return it
            solutionPath = getPath(currentNode);
            fringe = []; // stop the loop
        } else {
            // not a solution, add the new reachable positions to the fringe
            for (i = 0; i < DIRECTIONS.length; i++) {
                direction = DIRECTIONS[i];
                if (!hasWall(currentNode.position, direction, walls)) {
                    addNode(currentNode, 
                            direction,
                            move(currentNode.position, 
                                 direction, 
                                 gridSize, 
                                 walls),
                            currentNode.cost + 1,
                            step);
                }
            }
        }
    }

    return {
        path: solutionPath, 
        tree: searchTree,
        grid: nodesGrid,
        lastStep: step
    };
}


// Create a landmark object with costs information.
// Calculate the distances from the specified landmark to all other positions, 
// return a grid with that information.
// This uses breadth first search, because we *know* that all actions have the
// same cost, and so breadth first behaves like uniform cost or dijkstra, 
// yielding the optimal cost to each node.
function createLandmark(landmarkPosition, gridSize, walls) {
    var fringe = [],
        costsGrid = createTable(gridSize, null),
        currentNode, newNode, i, direction;

    // searchGrid will contain the cost from the startingPosition to each 
    // position as an array

    // add a new node to the fringe
    function addNode(position, cost) {
        if (costsGrid[position.x][position.y] !== null) {
            return; // already visited
        }

        newNode = {
            position: position, 
            cost: cost,
        };

        // add at begining, because search algorithm extracts from the tail
        fringe.unshift(newNode);

        // store the cost in the costs grid
        costsGrid[position.x][position.y] = cost;
    }

    // root of the search tree
    addNode(landmarkPosition, 0);
 
    // search loop
    while (fringe.length > 0) {    
        currentNode = fringe.pop();

        // add the new reachable positions to the fringe
        for (i = 0; i < DIRECTIONS.length; i++) {
            direction = DIRECTIONS[i];
            if (!hasWall(currentNode.position, direction, walls)) {
                addNode(move(currentNode.position, 
                             direction, 
                             gridSize, 
                             walls),
                        currentNode.cost + 1);
            }
        }
    }

    return {
        position: landmarkPosition,    
        costs: costsGrid
    }
}


// the actual agent
function agentFunction(perception) {
    var direction, randomChoice, pathSolution, landmarks, i;

    // on the first step, do the landmarks distances pre-calculation. Store 
    // it in meta to avoid re-calculating it each step
    // on the next steps, just get it from the meta
    if (this.meta && this.meta.landmarks) {
        landmarks = this.meta.landmarks;
    } else {
        landmarks = [];
        for (i = 0; i < perception.landmarks.length; i++) {
            landmarks.push(createLandmark(perception.landmarks[i], 
                                          perception.gridSize, 
                                          perception.walls));
        }
    }

    pathSolution = aStarPath(perception.me, 
                             perception.flag,
                             perception.gridSize, 
                             perception.walls,
                             landmarks);

    // when a path is found, the first element is the initial node, with no 
    // previous action. A path of 1 element means we are already at the flag

    if (pathSolution.path === null || pathSolution.path.length === 1) {
        // at the flag, or no path to the flag. Choose a random direction
        randomChoice = Math.floor(Math.random() * DIRECTIONS.length);
        direction = DIRECTIONS[randomChoice];
    } else {
        // there is a path to the flag, choose the first action on that path
        direction = pathSolution.path[1].action;
    }

    // store metadata to use in the visualization
    this.meta = {
        solutionPath: pathSolution.path,
        searchTree: pathSolution.tree,
        searchGrid: pathSolution.grid,
        searchLastStep: pathSolution.lastStep,
        landmarks: landmarks
    };

    // return a single action, moving in the decided direction
    return new values.Move({'direction': new values[direction]()});
}

agent.run(agentFunction);
