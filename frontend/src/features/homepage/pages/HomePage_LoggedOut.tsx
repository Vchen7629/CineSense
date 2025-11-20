import "../../../shared/styles/App.css";
import Header from "../../navbar/components/Header";

export default function HomePage() {
  return (
    <main style={{ backgroundColor: "#879B9E", minHeight: "100vh" }}>
      <Header />

      {/* bacground*/}
      <div
        style={{
          borderTop: "#000000ff",
          background: "#2E454D",
          color: "#FFFFFF",
          textAlign: "center",
          padding: "90px 30px",
          boxShadow: "0 10px 18px rgba(0,0,0,0.25)",
        }}
      >
        <h1
          style={{
            fontFamily: "Inter, sans-serif",
            fontWeight: "bold",
            fontSize: "40px",
            marginTop: "12px",
            marginBottom: "30px",
          }}
        >
          Smarter Movie
          <br />
          Recommendations
        </h1>

        {/*subtitle*/}
        <p
          style={{
            fontFamily: "inter, sans-serif",
            fontSize: "30px",
            lineHeight: "1.4",
            margin: 0,
            color: "#E8ECEE",
          }}
        >
          Movie Recommendations powered by collaborative Filtering
        </p>
      </div>

      {/* how it works  and the Cards*/}
      <div style={{ padding: "40px 24px 72px" }}>
        <h2
          style={{
            textAlign: "center",
            color: "#2E454D",
            fontWeight: 400,
            fontSize: "30px",
            margin: "0 0 28px 0",
          }}
        >
          How it works
        </h2>

        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "24px",
            flexWrap: "wrap",
            maxWidth: "1100px",
            margin: "0 auto",
          }}
        >
          {/*CARD 1*/}
          <div
            style={{
              backgroundColor: "#2E454D",
              color: "#FFFFFF",
              borderRadius: "14px",
              boxShadow: "0 6px 12 px rgba(0,0,0,0.25)",
              width: "320px",
              padding: "22px",
              textAlign: "center",
            }}
          >
            <div
              style={{
                fontSize: "40px",
                marginBottom: "12px",
                opacity: 0.9,
              }}
            >
              👤
            </div>
            <h3
              style={{
                fontFamily: "Inter, sans-serif",
                fontWeight: 600,
                fontSize: "16px",
                margin: "0 0 6px 0",
              }}
            >
              1. Sign Up With a User Account
            </h3>
            <p
              style={{
                fontFamily: "Inter, sans-serif",
                fontSize: "13px",
                color: "#D6DADF",
                margin: 0,
              }}
            >
              Add your genre preferences and movie watch list ratings.
            </p>
          </div>

          {/* card 2 */}
          <div
            style={{
              backgroundColor: "#2E454D",
              color: "#FFFFFF",
              borderRadius: "14px",
              boxShadow: "0 6px 12px rgba(0,0,0,0.25)",
              width: "320px",
              padding: "22px",
              textAlign: "center",
            }}
          >
            <div
              style={{ fontSize: "40px", marginBottom: "12px", opacity: 0.9 }}
            >
              🎬
            </div>
            <h3
              style={{
                fontFamily: "Inter, sans-serif",
                fontWeight: 600,
                fontSize: "16px",
                margin: "0 0 6px 0",
              }}
            >
              2. New Movie Recommendations
            </h3>
            <p
              style={{
                fontFamily: "Inter, sans-serif",
                fontSize: "13px",
                color: "#D6DADF",
                margin: 0,
              }}
            >
              We recommend movies based on your preferences and ratings.
            </p>
          </div>

          {/* card 3 */}
          <div
            style={{
              backgroundColor: "#2E454D",
              color: "#FFFFFF",
              borderRadius: "14px",
              boxShadow: "0 6px 12px rgba(0,0,0,0.25)",
              width: "320px",
              padding: "22px",
              textAlign: "center",
            }}
          >
            <div
              style={{ fontSize: "40px", marginBottom: "12px", opacity: 0.9 }}
            >
              👍
              <h3
                style={{
                  fontFamily: "Inter, sans-serif",
                  fontWeight: 600,
                  fontSize: "16px",
                  margin: "0 0 6px 0",
                }}
              >
                3. Rate Recommendations
              </h3>
              <p
                style={{
                  fontFamily: "Inter, sans-serif",
                  fontSize: "13px",
                  color: "#D6DADF",
                  margin: 0,
                }}
              >
                As you rate, the system adapts and finds closer matches.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* <div className="flex h-[90vh] w-full justify-center items-center ">
        <p className="text-white text-3xl"> Home Page </p>
      </div> */}
    </main>
  );
}
