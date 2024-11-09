package main

import (
	"encoding/json"
	"html/template"
	"log"
	"net/http"
)

type User struct {
	Username     string
	Subscription string
}

var user = User{Username: "john_doe", Subscription: "Free"}

func main() {
	http.HandleFunc("/", serveTemplate)
	http.HandleFunc("/login", login)
	http.HandleFunc("/get-username", getUsername)
	http.HandleFunc("/get-editable-username", getEditableUserName)
	http.HandleFunc("/update-username", updateUsername)
	http.HandleFunc("/get-subscription", getSubscription)
	http.HandleFunc("/toggle-subscription", toggleSubscription)

	log.Println("Server started on http://localhost:8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func serveTemplate(w http.ResponseWriter, r *http.Request) {
	tmpl := template.Must(template.ParseFiles("templates/index.html"))
	tmpl.Execute(w, nil)
}

func login(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()

	if r.FormValue("email") == "colin@colin.com" && r.FormValue("password") == "password" {
		tmpl := template.Must(template.ParseFiles("templates/userPage.html"))
		tmpl.Execute(w, nil)
	}
}

// Get current username
func getUsername(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte(user.Username))
}

func getEditableUserName(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte(`<span id="username-display"><form hx-post="/update-username" hx-target="#username-display" hx-swap="outerHTML">
	<input type="text" name="username" placeholder="Enter new username" required>
	<button type="submit">Save</button>
  </form></span>`))
}

// Update username
func updateUsername(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	user.Username = r.FormValue("username")
	w.Write([]byte(`<span id="username-display">` + user.Username + `</span>`)) // Send updated username back to client
}

// Get current subscription
func getSubscription(w http.ResponseWriter, r *http.Request) {
	response, _ := json.Marshal(map[string]string{"subscription": user.Subscription})
	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(`<span id="subscription-display">` + user.Subscription + `</span>`))
	print(response)
}

// Toggle subscription
func toggleSubscription(w http.ResponseWriter, r *http.Request) {
	if user.Subscription == "Free" {
		user.Subscription = "Paid"
	} else {
		user.Subscription = "Free"
	}
	w.Write([]byte(`<span id="subscription-display">` + user.Subscription + `</span>`))
}
