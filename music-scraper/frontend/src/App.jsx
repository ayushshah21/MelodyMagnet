import { useState } from "react";
import "./App.css";
import { ThreeDots } from "react-loader-spinner";

function App() {
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false); // State to track loading status

  const handleDownload = async (e) => {
    e.preventDefault();
    setIsLoading(true); // Start loading
    // const baseURL = "http://18.222.122.47:80/";
    const baseURL = "http://127.0.0.1:5000/"
    const playlistID = url.split("pl.u-")[1];
    const playlistName = url.split("/")[5];
    try {
      const response = await fetch(
        `${baseURL}?playlist_id=${encodeURIComponent(playlistID)}&playlist_name=${encodeURIComponent(playlistName)}`,
        {
          method: "GET",
        }
      );
      if (response.ok) {
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = downloadUrl;
        link.setAttribute("download", "songs.zip");
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
        const playlistID = url.split("pl.u-")[1];
        await handleCleanup(playlistID);
      } else {
        console.error("Failed to download songs");
      }
    } catch (error) {
      console.error("Error:", error);
    }
    setIsLoading(false); // End loading
  };

  const handleCleanup = async (playlistID) => {
    try {
      await fetch(`http://127.0.0.1:5000/cleanup/${playlistID}`, {
        method: "GET",
      });
    } catch (error) {
      console.error("Error during cleanup:", error);
    }
  };

  return (
    <>
      <h1>🎶 MelodyMagnet 🎶</h1>
      <p>Enter the URL of your Apple Music Playlist below, and download all its tracks as MP3 files directly to your device.</p>
      <div className="container">
        <div className="container__item">
          <form className="form" onSubmit={handleDownload}>
            <input
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              type="text"
              className="form__field"
              placeholder="Enter URL Here"
            />
            <div className="button-or-loader">
              {!isLoading ? (
                <button type="submit" className="btn btn--primary uppercase">
                  Download Songs
                </button>
              ) : (
                <ThreeDots
                  color="#61DAFB" // Spinner color
                  height={80}
                  width={80}
                />
              )}
            </div>
          </form>
        </div>
      </div>
    </>
  );
}

export default App;
