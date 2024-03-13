import { useState } from "react";
import "./App.css";

function App() {
  const [url, setUrl] = useState("");
  const handleDownload = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/?playlist_url=${encodeURIComponent(url)}`,
        {
          method: "GET",
        }
      );
      if (response.ok) {
        // Create a Blob from the response
        const blob = await response.blob();
        // Create an anchor element and trigger download
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = downloadUrl;
        link.setAttribute("download", "songs.zip"); // Set the file name
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
        const playlistID = url.split('pl.u-')[1];
        handleCleanup(playlistID);
      } else {
        console.error("Failed to download songs");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

const handleCleanup = async (playlistID) => {
  try {
    const response = await fetch(`http://127.0.0.1:5000/cleanup/${playlistID}`, {
      method: 'GET',
    });
    if (response.ok) {
      console.log('Cleanup successful');
    } else {
      console.error('Cleanup failed');
    }
  } catch (error) {
    console.error('Error:', error);
  }

}

  return (
    <>
      <h1>🎶 MelodyMagnet 🎶</h1>
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
            <div className="button-container">
              <button type="submit" className="btn btn--primary uppercase">
                Download Songs
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}

export default App;
