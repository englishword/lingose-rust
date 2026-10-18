require "json"

class Lingose < Formula
  desc "Offline English word queries and plain-text IPS annotation"
  homepage "https://lingose.com/"
  version "0.2.0"
  license "CC-BY-4.0"

  depends_on :macos

  on_macos do
    on_arm do
      url "https://github.com/englishword/lingose-rust/releases/download/v0.2.0/lingose-v0.2.0-macos-aarch64.tar.gz"
      sha256 "28c1067255acc4bc3be023e976adf708b6885a1d0e53d144aae8d0bcf6d04755"
    end
    on_intel do
      url "https://github.com/englishword/lingose-rust/releases/download/v0.2.0/lingose-v0.2.0-macos-x86_64.tar.gz"
      sha256 "56e039f17e50a32a21d35dece6da20ce429dec8b4936565556e49a510191b4dd"
    end
  end

  livecheck do
    url "https://github.com/englishword/lingose-rust"
    strategy :github_latest
  end

  def install
    bin.install "lingose"
    # Preserve the complete set of redistribution notices and audit metadata.
    pkgshare.install "LICENSE", "SOURCES.md", "README.md", "manifest.json", "sources", "licenses"
  end

  def caveats
    <<~EOS
      These upstream binaries were validated on macOS 15.7.9.
      Developer ID signing, notarization and browser Gatekeeper acceptance are not provided.
      Third-party terms and provenance limits: #{pkgshare}/SOURCES.md
    EOS
  end

  test do
    assert_equal "lingose 0.2.0\n", shell_output("#{bin}/lingose --version")
    expected = { "word" => "apple", "ipa" => ["æpəl"], "ips" => ["apple"],
                 "ism" => "app-le", "ipsm" => ["app-le"], "root_lemma" => "ap" }
    assert_equal expected, JSON.parse(shell_output("#{bin}/lingose word apple --json"))
    text = "Abandon the book.\n"
    output = pipe_output("#{bin}/lingose annotate --json", text, 0)
    assert_equal({ "text" => text, "annotate" => "Åbando\u030An \u1E6Bhe\u030A book.\n" }, JSON.parse(output))
  end
end
