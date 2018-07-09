package neuralknight

import (
	"net/http"
	"regexp"

	"github.com/neuralknight/neuralknight/neuralknight/views"
)

// Handler neuralknight
type Handler struct{}

var routerHome = regexp.MustCompile("^/?$")
var routerV1 = regexp.MustCompile("^api/v1.0/")
var routerV1Games = regexp.MustCompile("^api/v1.0/games")
var routerV1Agents = regexp.MustCompile("^api/v1.0/agents")

func (f Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if routerV1.MatchString(r.URL.Path) {
		if routerV1Games.MatchString(r.URL.Path) {
			neuralknightviews.ServeAPIGamesHTTP(w, r)
			return
		}
		if routerV1Agents.MatchString(r.URL.Path) {
			neuralknightviews.ServeAPIAgentsHTTP(w, r)
			return
		}
	} else if routerHome.MatchString(r.URL.Path) {
	}
	http.NotFound(w, r)
}

// import os
// from pyramid.config import Configurator
//
// testapp = None
//
//
// def main(global_config, **settings):
//     """
//     Return a Pyramid WSGI application.
//     """
//     if os.environ.get("DATABASE_URL", ""):
//         settings["sqlalchemy.url"] = os.environ["DATABASE_URL"]
//     else:
//         settings["sqlalchemy.url"] = "postgres://localhost:5432/neuralknight"
//     if os.environ.get("PORT", ""):
//         settings["listen"] = "*:" + os.environ["PORT"]
//     else:
//         settings["listen"] = "localhost:8080"
//     config = Configurator(settings=settings)
//     config.include("cornice")
//     config.include("pyramid_jinja2")
//     config.include(".models")
//     config.include(".routes")
//      config.include(".security")
//     config.scan()
//     return config.make_wsgi_app()
// def includeme(config):
//     config.add_static_view("static", "static", cache_max_age=3600)
//     config.add_route("home", "/")
