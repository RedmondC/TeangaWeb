package main

import (
	"errors"
	"log/slog"
	"net/http"

	"teangaWeb/templates"

	"github.com/a-h/templ"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

func main() {
	e := echo.New()

	// Middleware
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())

	e.Static("/assets", "assets")
	e.GET("/", basicLayout)
	//e.GET("/*", RouteNotFoundHandler) 404 page

	if err := e.Start(":8080"); err != nil && !errors.Is(err, http.ErrServerClosed) {
		slog.Error("failed to start server", "error", err)
	}
}

func basicLayout(c echo.Context) error {
	return renderView(c, templates.BasicInfoLayout())
}

func renderView(c echo.Context, cmp templ.Component) error {
	c.Response().Header().Set(echo.HeaderContentType, echo.MIMETextHTML)

	return cmp.Render(c.Request().Context(), c.Response().Writer)
}
