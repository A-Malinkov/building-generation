"""Convert the downloaded 3D BAG pages (CityJSON) into one OBJ file for Houdini.
Origin (0,0,0) = the site, Schiestraat 11 (RD 92247.5, 437869.7). Houdini axes: X = east, Z = south, Y = up.
Run:  python3 convert_3dbag_to_obj.py   (from this folder)"""
import glob, json, os
this_folder = os.path.dirname(os.path.abspath(__file__))
ORIGIN_EAST, ORIGIN_NORTH = 92247.5, 437869.7   # Schiestraat 11 in RD coordinates
LEVEL_OF_DETAIL = "2.2"   # 3D BAG detail level: 1.2 = simple blocks, 2.2 = with roof shapes

obj_lines, vertex_count, building_part_count = [], 0, 0
for page_file in sorted(glob.glob(os.path.join(this_folder, "page_*.json"))):
    page = json.load(open(page_file))
    scale = page["metadata"]["transform"]["scale"]
    translate = page["metadata"]["transform"]["translate"]
    for feature in page["features"]:
        # CityJSON stores whole numbers; scale and translate turn them back into RD coordinates
        vertices = [(v[0] * scale[0] + translate[0], v[1] * scale[1] + translate[1], v[2] * scale[2] + translate[2])
                    for v in feature["vertices"]]
        for city_object in feature["CityObjects"].values():
            for geometry in city_object.get("geometry", []):
                if str(geometry["lod"]) != LEVEL_OF_DETAIL:
                    continue
                building_part_count += 1
                obj_index_of = {}   # vertex index in the page -> vertex number in the OBJ
                for shell in geometry["boundaries"]:
                    for surface in shell:
                        outer_ring = surface[0]               # outer ring only
                        for vertex_index in outer_ring:
                            if vertex_index not in obj_index_of:
                                east, north, height = vertices[vertex_index]
                                obj_lines.append(f"v {east - ORIGIN_EAST:.3f} {height:.3f} {-(north - ORIGIN_NORTH):.3f}")
                                vertex_count += 1
                                obj_index_of[vertex_index] = vertex_count
                        obj_lines.append("f " + " ".join(str(obj_index_of[vertex_index]) for vertex_index in outer_ring))
open(os.path.join(this_folder, "..", "surroundings_3dbag.obj"), "w").write("\n".join(obj_lines))
print(building_part_count, "building parts,", vertex_count, "vertices")
