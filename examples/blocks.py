"""
Example file showing a demo with 100 agents split in four groups initially positioned in four corners of the environment. Each agent attempts to move to other side of the environment through a narrow passage generated by four obstacles. There is no roadmap to guide the agents around the obstacles.
"""
import math
import random
import gym.envs.classic_control.rendering as rendering

import rvo.math as rvo_math

from rvo.vector import Vector2
from rvo.simulator import Simulator

RVO_OUTPUT_TIME_AND_POSITIONS = True
RVO_SEED_RANDOM_NUMBER_GENERATOR = True


class Blocks:

    def __init__(self):
        self.goals_ = [] # Vector2

        if RVO_SEED_RANDOM_NUMBER_GENERATOR:
            random.seed()
        else:
            random.seed(0)

        self.simulator_ = Simulator()

    def setupScenario(self):
        # Specify the global time step of the simulation.
        self.simulator_.setTimeStep(0.25)

        # Specify the default parameters for agents that are subsequently added.
        self.simulator_.setAgentDefaults(15.0, 10, 5.0, 5.0, 2.0, 2.0, Vector2(0.0, 0.0))

        # Add agents, specifying their start position, and store their goals on the opposite side of the environment.
        for i in range(5):
            for j in range(5):
                self.simulator_.addAgent(Vector2(55.0 + i * 10.0, 55.0 + j * 10.0))
                self.goals_.append(Vector2(-75.0, -75.0))

                self.simulator_.addAgent(Vector2(-55.0 - i * 10.0, 55.0 + j * 10.0))
                self.goals_.append(Vector2(75.0, -75.0))

                self.simulator_.addAgent(Vector2(55.0 + i * 10.0, -55.0 - j * 10.0))
                self.goals_.append(Vector2(-75.0, 75.0))

                self.simulator_.addAgent(Vector2(-55.0 - i * 10.0, -55.0 - j * 10.0))
                self.goals_.append(Vector2(75.0, 75.0))

        # Add (polygonal) obstacles, specifying their vertices in counterclockwise order.
        obstacle1 = []
        obstacle1.append(Vector2(-10.0, 40.0))
        obstacle1.append(Vector2(-40.0, 40.0))
        obstacle1.append(Vector2(-40.0, 10.0))
        obstacle1.append(Vector2(-10.0, 10.0))
        self.simulator_.addObstacle(obstacle1)

        obstacle2 = []
        obstacle2.append(Vector2(10.0, 40.0))
        obstacle2.append(Vector2(10.0, 10.0))
        obstacle2.append(Vector2(40.0, 10.0))
        obstacle2.append(Vector2(40.0, 40.0))
        self.simulator_.addObstacle(obstacle2)

        obstacle3 = []
        obstacle3.append(Vector2(10.0, -40.0))
        obstacle3.append(Vector2(40.0, -40.0))
        obstacle3.append(Vector2(40.0, -10.0))
        obstacle3.append(Vector2(10.0, -10.0))
        self.simulator_.addObstacle(obstacle3)

        obstacle4 = []
        obstacle4.append(Vector2(-10.0, -40.0))
        obstacle4.append(Vector2(-10.0, -10.0))
        obstacle4.append(Vector2(-40.0, -10.0))
        obstacle4.append(Vector2(-40.0, -40.0))
        self.simulator_.addObstacle(obstacle4)

        # Process the obstacles so that they are accounted for in the simulation.
        self.simulator_.processObstacles()

    def updateVisualization(self, viewer):
        if not RVO_OUTPUT_TIME_AND_POSITIONS:
            return

        # Output the current global time.
        global_time = self.simulator_.getGlobalTime()

        # Render the current position of all the agents.
        colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
        for i in range(self.simulator_.getNumAgents()):
            position = self.simulator_.getAgentPosition(i)
            color = colors[i % len(colors)]
            circle = viewer.draw_circle(radius=self.simulator_.defaultAgent_.radius_, color=color)
            circle.add_attr(rendering.Transform(translation=(position.x, position.y)))

        viewer.render()

    def setPreferredVelocities(self):
        # Set the preferred velocity to be a vector of unit magnitude (speed) in the direction of the goal.
        for i in range(self.simulator_.getNumAgents()):
            goalVector = self.goals_[i] - self.simulator_.getAgentPosition(i)

            if rvo_math.absSq(goalVector) > 1.0:
                goalVector = rvo_math.normalize(goalVector)

            self.simulator_.setAgentPrefVelocity(i, goalVector)

            # Perturb a little to avoid deadlocks due to perfect symmetry.
            angle = random.random() * 2.0 * math.pi
            dist = random.random() * 0.0001

            self.simulator_.setAgentPrefVelocity(i, self.simulator_.getAgentPrefVelocity(i) +
                dist * Vector2(math.cos(angle), math.sin(angle)))

    def reachedGoal(self):
        # Check if all agents have reached their goals.
        for i in range(self.simulator_.getNumAgents()):
            if rvo_math.absSq(self.simulator_.getAgentPosition(i) - self.goals_[i]) > 400.0:
                return False
        return True


def main():
    viewer = rendering.Viewer(600, 600)
    viewer.set_bounds(-300, 300, -300, 300)

    blocks = Blocks()

    # Set up the scenario.
    blocks.setupScenario()

    # Perform (and manipulate) the simulation.
    while not blocks.reachedGoal():
        if RVO_OUTPUT_TIME_AND_POSITIONS:
            blocks.updateVisualization(viewer)
        blocks.setPreferredVelocities()
        blocks.simulator_.doStep()


if __name__ == '__main__':
    main()