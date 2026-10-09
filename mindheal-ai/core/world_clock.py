import streamlit.components.v1 as components


# =========================================================
# MINDHEAL WORLD CLOCK
# =========================================================

def render_world_clock():

    components.html(
        """
        <!DOCTYPE html>

        <html>

        <head>

            <meta charset="UTF-8">

            <style>

                * {
                    box-sizing: border-box;
                }

                html,
                body {
                    margin: 0;
                    padding: 0;
                    background: transparent;

                    font-family:
                        "Segoe UI",
                        Arial,
                        sans-serif;
                }

                .clock-row {

                    width: 100%;

                    margin: 10px auto 4px auto;

                    display: flex;

                    align-items: center;

                    justify-content: space-between;

                    gap: 10px;

                    padding: 11px 10px;

                    border-top:
                        1px solid #E5ECE7;

                    border-bottom:
                        1px solid #E5ECE7;

                    color: #53675D;

                    white-space: nowrap;
                }


                .clock-item {

                    display: flex;

                    align-items: baseline;

                    gap: 7px;

                    min-width: 0;
                }


                .clock-city {

                    font-size: 0.95rem;

                    font-weight: 600;

                    color: #53675D;
                }


                .clock-time {

                    font-size: 1.0rem;

                    font-weight: 800;

                    color: #234B39;
                }


                .clock-separator {

                    color: #B8C5BE;

                    font-size: 0.9rem;

                    font-weight: 600;
                }


                /* Smaller screens */

                @media (max-width: 900px) {

                    .clock-row {

                        gap: 6px;

                        padding:
                            9px 5px;
                    }

                    .clock-city {

                        font-size:
                            0.82rem;
                    }

                    .clock-time {

                        font-size:
                            0.86rem;
                    }

                    .clock-separator {

                        font-size:
                            0.72rem;
                    }
                }


                /* Mobile */

                @media (max-width: 650px) {

                    .clock-row {

                        white-space:
                            normal;

                        flex-wrap:
                            wrap;

                        justify-content:
                            flex-start;

                        row-gap:
                            8px;
                    }

                    .clock-separator {

                        display:
                            none;
                    }

                    .clock-item {

                        width:
                            calc(50% - 6px);
                    }
                }

            </style>

        </head>


        <body>

            <div class="clock-row">


                <div class="clock-item">

                    <span class="clock-city">
                        🌍 Los Angeles
                    </span>

                    <span
                        class="clock-time"
                        id="los-angeles">
                    </span>

                </div>


                <span class="clock-separator">
                    |
                </span>


                <div class="clock-item">

                    <span class="clock-city">
                        Berlin
                    </span>

                    <span
                        class="clock-time"
                        id="berlin">
                    </span>

                </div>


                <span class="clock-separator">
                    |
                </span>


                <div class="clock-item">

                    <span class="clock-city">
                        Sydney
                    </span>

                    <span
                        class="clock-time"
                        id="sydney">
                    </span>

                </div>


                <span class="clock-separator">
                    |
                </span>


                <div class="clock-item">

                    <span class="clock-city">
                        New York
                    </span>

                    <span
                        class="clock-time"
                        id="new-york">
                    </span>

                </div>


            </div>


            <script>

                const clocks = [

                    {
                        id: "los-angeles",
                        timezone:
                            "America/Los_Angeles"
                    },

                    {
                        id: "berlin",
                        timezone:
                            "Europe/Berlin"
                    },

                    {
                        id: "sydney",
                        timezone:
                            "Australia/Sydney"
                    },

                    {
                        id: "new-york",
                        timezone:
                            "America/New_York"
                    }

                ];


                function updateClocks() {

                    clocks.forEach(
                        clock => {

                            const formatter =
                                new Intl.DateTimeFormat(
                                    "en-US",
                                    {
                                        timeZone:
                                            clock.timezone,

                                        hour:
                                            "numeric",

                                        minute:
                                            "2-digit",

                                        hour12:
                                            true
                                    }
                                );


                            document
                                .getElementById(
                                    clock.id
                                )
                                .textContent =
                                    formatter.format(
                                        new Date()
                                    );

                        }
                    );

                }


                updateClocks();


                setInterval(
                    updateClocks,
                    1000
                );

            </script>

        </body>

        </html>
        """,

        height=66,

        scrolling=False,
    )
