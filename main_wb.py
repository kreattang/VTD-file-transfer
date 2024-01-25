import os
from scenariogeneration import xosc, prettyprint, ScenarioGenerator
import time
import json
from utils.vehiclesetting import lane_change, create_vechicle, init_vehicle, setup_ego, setup_npc
from utils.options import arg_parse
from utils.scpcmd import load_xosc, scp_generate, scp_run
import subprocess
import time
import asyncio
import sys


class Scenario(ScenarioGenerator):
    def __init__(self, args, testcase):
        super().__init__()
        self.open_scenario_version = 2
        self.args = args
        self.testcase = testcase

    def scenario(self, **kwargs):
        
        catalog = xosc.Catalog()

        catalog.add_catalog("VehicleCatalog", self.testcase["VehicleCatalog"])
        catalog.add_catalog("ControllerCatalog", self.testcase["ControllerCatalog"])
        catalog.add_catalog("PedestrianCatalog", self.testcase["PedestrianCatalog"])

        road = xosc.RoadNetwork(
            roadfile=self.testcase["roadfile"], scenegraph=self.testcase["scenegraph"]
        )

        paramdec = xosc.ParameterDeclarations()
        entities = xosc.Entities()
        init = xosc.Init()

        storylist = []
        ego = self.testcase["ego"]
        
        storylist.append(setup_ego(ego, entities, init))


        for npc in self.testcase.get("npcList", []):
            npcstory = setup_npc(npc, entities, init)
            if npcstory is not None:
                storylist.append(npcstory)
        
        ## create the storyboard
        sb = xosc.StoryBoard(
            init,
            xosc.ValueTrigger(
                "stop_simulation",
                0,
                xosc.ConditionEdge.rising,
                xosc.SimulationTimeCondition(self.testcase["duration"], xosc.Rule.greaterThan),
                "stop",
            ),
        )

        for s in storylist:
            sb.add_story(s)

        ## create the scenario
        sce = xosc.Scenario(
            self.testcase["ScenarioName"],
            "User",
            paramdec,
            entities=entities,
            storyboard=sb,
            roadnetwork=road,
            catalog=catalog,
            osc_minor_version=self.open_scenario_version,
        )
        return sce


if __name__ == "__main__":
    args = arg_parse()
    testcase_path = args.testcasepath + args.testcase
    try:
        with open(testcase_path, "r") as json_file:
            testcase = json.load(json_file)    
    except FileNotFoundError:
        print(f"File not found: {testcase_path}")
        sys.exit(1)
    
    # create openscenario file
    sce = Scenario(args, testcase)
    scenario_files, road_files = sce.generate(args.xoscpath)
    print("OpenScenario file generated:")
    print(scenario_files)



    # generate run scp file
    start_process = [
        ["wait", "init"],
        ["+1", "start"],
        ["+40s", "stop"]
    ]

    param = [start_process[-1][0][1:-1]]
    subprocess.call(["python", "receive.py"] + param)

    start_process.insert(0, ["0", load_xosc(scenario_files[0])])

    # scp process generatation
    scp_generate(args.scpfile, start_process)

    print("Successfully create scp file:" + args.scpfile)


    # run generated scp file
    print("Running")
    p = asyncio.run(scp_run(scp_path=args.scpgenpath, filename=args.scpfile))

    # stdout = p.stdout.decode('utf-8')
    print(p.stdout)
    
