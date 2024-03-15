import { useState } from "react";
import "./App.css";
import { ThreeDots } from "react-loader-spinner";

function App() {
  const [url, setUrl] = useState("");
  const [isValidUrl, setIsValidUrl] = useState(true); // State to track URL validity
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");

  const validateUrl = (inputUrl) => {
    const appleMusicRegex =
      /^https:\/\/music\.apple\.com\/us\/playlist\/.+\/pl\.u-[a-zA-Z0-9]+$/;
    // const spotifyRegex =
    //   /^https:\/\/open\.spotify\.com\/playlist\/[a-zA-Z0-9]+(\?si=[a-zA-Z0-9]+)?$/;
    return appleMusicRegex.test(inputUrl);
    // || spotifyRegex.test(inputUrl)
  };

  const handleDownload = async (e) => {
    e.preventDefault();

    setUrl("");
    if (!validateUrl(url)) {
      setIsValidUrl(false);
      return;
    }

    setIsValidUrl(true);
    setIsLoading(true);
    setLoadingMessage("Getting started...");

    const isAppleMusic = url.includes("music.apple.com");
    const isSpotify = url.includes("open.spotify.com");
    const streamingType = isAppleMusic
      ? "apple"
      : isSpotify
      ? "spotify"
      : "";

    // const baseURL = "http://18.222.122.47:80/"; // Update this to your actual backend URL
    const baseURL = "http://127.0.0.1:5000"
    // const playlistID = url.split("pl.u-")[1];
    // const playlistName = url.split("/")[5];

    const playlistID = isAppleMusic ? url.split("pl.u-")[1] : isSpotify ? url.split("playlist/")[1] : "";
    const playlistName = isAppleMusic ? url.split("/")[5] : "Spotify Playlist"; // Modify as needed for Spotify

    try {
      setLoadingMessage("Fetching playlist...");

      const response = await fetch(
        `${baseURL}?playlist_id=${encodeURIComponent(playlistID)}&playlist_name=${encodeURIComponent(playlistName)}&streaming_type=${encodeURIComponent(streamingType)}`,
        {
          method: "GET",
        }
      );

      if (response.ok) {
        setLoadingMessage("Preparing download...");

        setTimeout(async () => {
          const blob = await response.blob();
          const downloadUrl = window.URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = downloadUrl;
          link.setAttribute("download", "songs.zip");
          document.body.appendChild(link);
          link.click();
          link.parentNode.removeChild(link);

          setLoadingMessage("Download ready!");

          setTimeout(() => {
            setIsLoading(false);
            setLoadingMessage("");
          }, 2000);
        }, 1000);
      } else {
        console.error("Failed to download songs");
        setIsLoading(false);
        setLoadingMessage("");
      }
    } catch (error) {
      console.error("Error:", error);
      setIsLoading(false);
      setLoadingMessage("");
    }
  };

  return (
    <>
      <h1>🎶 MelodyMagnet 🎶</h1>
      <p>
        Enter the URL of your Apple Music Playlist below, and download all its
        tracks as MP3 files directly to your device.
      </p>
      <div className="container">
        <div className="container__item">
          {!isLoading ? (
            <form className="form" onSubmit={handleDownload}>
              <input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                type="text"
                className={`form__field ${!isValidUrl ? "invalid" : ""}`}
                placeholder={!isValidUrl ? "Invalid URL!" : "Enter URL Here"}
              />
              <div className="button-container">
                <button type="submit" className="btn btn--primary uppercase">
                  Download Songs
                </button>
              </div>
            </form>
          ) : (
            <div className="loading-container">
              <ThreeDots color="#61DAFB" height={80} width={80} />
              <p className="loading-message">{loadingMessage}</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default App;
