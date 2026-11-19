"""Convert the downloaded 3D BAG pages (CityJSON) into one OBJ file for Houdini.
Origin (0,0,0) = the site, Schiestraat 11 (RD 92247.5, 437869.7). Houdini axes: X = east, Z = south, Y = up.
Run:  python3 convert_3dbag_to_obj.py   (from this folder)"""
import glob, json, os
here = os.path.dirname(os.path.abspath(__file__))
CX, CY = 92247.5, 437869.7
LOD = "2.2"   # 3D BAG detail level: 1.2 = simple blocks, 2.2 = with roof shapes

lines, nverts, nbuild = [], 0, 0
for page in sorted(glob.glob(os.path.join(here, "page_*.json"))):
    d = json.load(open(page))
    sc, tr = d["metadata"]["transform"]["scale"], d["metadata"]["transform"]["translate"]
    for feat in d["features"]:
        verts = [(v[0]*sc[0]+tr[0], v[1]*sc[1]+tr[1], v[2]*sc[2]+tr[2]) for v in feat["vertices"]]
        for obj in feat["CityObjects"].values():
            for g in obj.get("geometry", []):
                if str(g["lod"]) != LOD: continue
                nbuild += 1
                used = {}
                for shell in g["boundaries"]:
                    for surface in shell:
                        ring = surface[0]               # outer ring only
                        for i in ring:
                            if i not in used:
                                x, y, z = verts[i]
                                lines.append(f"v {x-CX:.3f} {z:.3f} {-(y-CY):.3f}")
                                nverts += 1; used[i] = nverts
                        lines.append("f " + " ".join(str(used[i]) for i in ring))
open(os.path.join(here, "..", "surroundings_3dbag.obj"), "w").write("\n".join(lines))
print(nbuild, "building parts,", nverts, "vertices")
