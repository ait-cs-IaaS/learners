#!/usr/bin/env python3

import os
import yaml
import sys, getopt


def main(argv):
    contentBaseDir = ""
    outputDir = ""
    config_file = ""

    try:
        opts, args = getopt.getopt(argv, "hi:o:c:", ["input=", "output=", "config="])
    except getopt.GetoptError:
        print("render_content.py -i <contentBaseDir> -o <outputDir> -c <configFile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("render_content.py -i <contentBaseDir> -o <outputDir> -c <configFile>")
            sys.exit()
        elif opt in ("-i", "--input"):
            contentBaseDir = arg
        elif opt in ("-o", "--output"):
            outputDir = arg
        elif opt in ("-c", "--config"):
            config_file = arg

    currentDir = os.getcwd()

    if not outputDir:
        outputDir = f"{currentDir}/rendered_hugo_content"

    if not contentBaseDir:
        print(
            "Please specify the content base directory (directory of the hugo files)\nrender_content.py -i <absolute path> or\nrender_content.py --input <absolute path>"
        )
        return

    if not config_file:
        config_file = os.getenv("LEARNERS_CONFIG") or os.path.join(currentDir, "learners_config.yml")

    learners_config = {}

    try:
        with open(config_file, "r") as stream:
            learners_config = yaml.safe_load(stream)
    except Exception as err:
        print(err)

    users = learners_config.get("users")

    for user, _ in users.items():
        for contentType in ["documentation", "exercises"]:

            # render hugo content
            command = "hugo"
            baseUrl = f"-b /statics/{contentType}"
            publishDir = f"-d {outputDir}/{contentType}/{user}"
            contentDir = f"-c {contentBaseDir}/content/{contentType}"
            if contentType == "documentation":
                config = f"--config {contentBaseDir}/base_config.yaml,{contentBaseDir}/docu_config.yaml"
            else:
                config = f"--config {contentBaseDir}/base_config.yaml,{contentBaseDir}/{contentType}_config.yaml"
            themesDir = f"--themesDir {contentBaseDir}/themes/"
            clean = "--cleanDestinationDir"

            print("-" * 100)
            print(f"Rendering hugo content for user: {user} ...")

            command = f"{command} {config} {baseUrl} {publishDir} {contentDir} {themesDir} {clean}"
            os.system(command)

            print(f"Rendered content: {publishDir}")
            print("-" * 100 + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
