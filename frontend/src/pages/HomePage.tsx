import type { ReactNode } from "react";
import { Link } from "react-router-dom";

type HomeTileProps = {
  to: string;
  ariaLabel: string;
  label: ReactNode;
  illustration: ReactNode;
  className?: string;
  heightClassName?: string;
  pillVariant?: "filled" | "outline";
  frameWidthClassName?: string;
  frameHeightClassName?: string;
};

function HomeTile({
  to,
  ariaLabel,
  label,
  illustration,
  className,
  heightClassName,
  pillVariant = "filled",
  frameWidthClassName = "w-[160px] md:w-[190px]",
  frameHeightClassName = "h-[90px] md:h-[110px]",
}: HomeTileProps) {
  const pillClassName =
    pillVariant === "outline"
      ? "bg-primary-700 border border-primary-700 text-white shadow-sm transition-colors duration-200 group-hover:bg-white group-hover:text-primary-800"
      : "bg-primary-700 border border-primary-700 text-white shadow-sm transition-colors duration-200 group-hover:bg-white group-hover:text-primary-800";

  return (
    <Link
      to={to}
      aria-label={ariaLabel}
      className={"group block focus:outline-none " + (className ?? "")}
    >
      <div className={heightClassName ?? "h-[190px] md:h-[205px] lg:h-[220px]"}>
        <div className="h-full rounded-[30px] bg-primary-100/70 border border-primary-200 shadow-sm flex flex-col items-center justify-between px-5 md:px-7 py-5 md:py-6">
          <div
            className={
              "rounded-2xl bg-primary-100/70 border border-primary-300 flex items-center justify-center transition-colors duration-200 hover:bg-white hover:border-primary-100 group-hover:bg-white group-hover:border-primary-100 " +
              frameWidthClassName +
              " " +
              frameHeightClassName
            }
          >
            <div className="text-5xl md:text-6xl leading-none select-none" aria-hidden>
              {illustration}
            </div>
          </div>

          <div
            className={
              "rounded-full px-8 md:px-10 py-3 md:py-3.5 text-center w-fit " + pillClassName
            }
          >
            <div className="text-base md:text-lg font-extrabold leading-snug whitespace-pre-line">
              {label}
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-primary-50">
      <div className="container mx-auto px-4 py-10 md:py-14">
        <div className="max-w-6xl mx-auto">
          <div className="relative rounded-[44px] bg-white/55 border border-primary-100 p-7 md:p-12 overflow-hidden">
            <div
              className="pointer-events-none absolute right-8 top-8 h-28 w-48 md:h-32 md:w-56 text-primary-200 opacity-60"
              style={{
                backgroundImage: "radial-gradient(currentColor 2px, transparent 2px)",
                backgroundSize: "14px 14px",
              }}
            />
            <div
              className="pointer-events-none absolute left-10 bottom-10 h-28 w-48 md:h-32 md:w-56 text-primary-200 opacity-55"
              style={{
                backgroundImage: "radial-gradient(currentColor 2px, transparent 2px)",
                backgroundSize: "14px 14px",
              }}
            />

            <div className="relative grid gap-8 lg:grid-cols-3 lg:grid-rows-2">
              {/* Banner: row 1, spans col 1-2 */}
              <Link
                to="/start"
                className="group block focus:outline-none lg:col-span-2 lg:row-start-1"
                aria-label="เริ่มแบบคัดกรองและประเมินภาวะโภชนาการ"
              >
                <div className="h-[190px] md:h-[205px] lg:h-[220px]">
                  <div className="h-full rounded-[32px] bg-primary-100/70 border border-primary-200 shadow-sm px-7 md:px-10 py-6 md:py-7">
                    <div className="h-full flex flex-col items-center justify-center text-center">
                      <div className="mb-4 md:mb-5 rounded-2xl bg-primary-100/70 border border-primary-300 w-[230px] md:w-[290px] h-[92px] md:h-[112px] flex items-center justify-center transition-colors duration-200 hover:bg-white hover:border-primary-100 group-hover:bg-white group-hover:border-primary-100">
                        <div className="text-5xl md:text-6xl leading-none select-none" aria-hidden>
                          👵👴🍲
                        </div>
                      </div>

                      <h1 className="max-w-[34ch] text-primary-800">
                        <span className="block text-[20px] md:text-[24px] lg:text-[26px] font-extrabold leading-[1.18] tracking-tight">
                          แบบคัดกรองและประเมินภาวะโภชนาการ
                        </span>
                        <span className="mt-1 block text-[18px] md:text-[20px] lg:text-[22px] font-extrabold leading-[1.2] tracking-tight">
                          ด้วยตนเองสำหรับผู้สูงอายุในชุมชน
                        </span>
                      </h1>
                    </div>
                  </div>
                </div>
              </Link>

              {/* Top-right: row 1 col 3 */}
              <div className="lg:col-start-3 lg:row-start-1">
                <HomeTile
                  to="/start"
                  ariaLabel="บันทึกการกิน"
                  label="บันทึกการกิน"
                  illustration={<span>📋</span>}
                  pillVariant="outline"
                />
              </div>

              {/* Bottom-left: row 2 col 1 */}
              <div className="lg:col-start-1 lg:row-start-2">
                <HomeTile
                  to="/knowledge"
                  ariaLabel="ความรู้เรื่องอาหาร"
                  label="ความรู้เรื่องอาหาร"
                  illustration={<span>📚</span>}
                />
              </div>

              {/* Bottom-middle: row 2 col 2 */}
              <div className="lg:col-start-2 lg:row-start-2">
                <HomeTile
                  to="/start"
                  ariaLabel="ประเมินความพึงพอใจ"
                  label="ประเมินความพึงพอใจ"
                  illustration={<span>💻</span>}
                />
              </div>

              {/* Bottom-right: row 2 col 3 */}
              <div className="lg:col-start-3 lg:row-start-2">
                <HomeTile
                  to="/facilities"
                  ariaLabel="ศูนย์บริการสาธารณสุข"
                  label="ศูนย์บริการสาธารณสุข"
                  illustration={<span>🏥</span>}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
