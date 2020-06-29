import graph_tool.all as gt


def color(label):
    options = ('b','g','r','c','m','y','k')
    return options[label%len(options)]


for g_name in ["youtube-S.gt"]:
    g = gt.load_graph(f"graphs/{g_name}")
    vertex_shape = g.new_vertex_property("string")
    vertex_pie_colors = g.new_vertex_property("vector<string>")
    vertex_pie_fractions = g.new_vertex_property("vector<double>")
    vertex_fill_color = g.new_vertex_property("vector<float>")
    for vtx in g.get_vertices():
        vertex_shape[vtx] = "pie" if len(g.vp.comm[vtx]) > 0 else "triangle"
        if vertex_shape[vtx] == "pie":
            vertex_pie_colors[vtx] = [color(label) for label in g.vp.comm[vtx]]
            vertex_pie_fractions[vtx] = [1/len(vertex_pie_colors[vtx]) for _ in vertex_pie_colors[vtx]]
        else:
            vertex_fill_color[vtx] = (0.6, 0.6, 0.6, 0.8)
    pos = gt.fruchterman_reingold_layout(g)
    gt.graph_draw(g, pos=pos, output_size=(8000,8000), output=f"{g_name[:g_name.find('.')]}-draw-frurei.png",
                  vertex_shape=vertex_shape, vertex_pie_colors=vertex_pie_colors, vertex_pie_fractions=vertex_pie_fractions,
                  vertex_fill_color=vertex_fill_color)
