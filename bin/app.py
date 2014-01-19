import web
import name_matching as nm

urls = (
  '/lookup', 'Index'
  )

app = web.application(urls, globals())

render = web.template.render('templates/',base="layout")

class Index(object):
    def GET(self):
        form = web.input(input_prospect=None)
        if form.input_prospect:
            matched = nm.get_top_three(form.input_prospect)
            return render.index(input_prospect=form.input_prospect,
                                matched_prospect=zip(*matched)[0],
                                score=[int(s*100)/100.0 for s in zip(*matched)[1]])
        else:
            return render.lookup_form()
#    def POST(self):
#        form = web.input(input_prospect=None)
#        matched = nm.Top3Getter(form.input_prospect)
#        #input_prospect = "%s, %s" % (matched[0][0],matched[0][1])
#        return render.index(matched_prospect=zip(*matched)[0],score=zip(*matched)[1])
		
if __name__ == "__main__":
    app.run()


##### just a place to test:
#db = web.database(dbn="redis",user=)


#matched = name_matching.top3Getter(form.input_prospect)
#input_prospect = "%s, %s" % (matched.keys(), matched.values())