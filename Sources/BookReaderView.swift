import MWDATCore
import SwiftUI

struct BookReaderView: View {
  @Environment(\.scenePhase) private var scenePhase
  @State private var camera = CameraViewModel(wearables: Wearables.shared)
  @State private var wearables = WearablesViewModel(wearables: Wearables.shared)
  @State private var reader = BookReaderModel()
  @AppStorage("summary-character-limit") private var limit = 200
  @State private var showSettings = false
  @State private var callbackError: String?

  var body: some View {
    NavigationStack {
      ScrollView {
        VStack(alignment: .leading, spacing: 18) {
          Text("本を見て、短く聴く")
            .font(.title.bold())
          Text("読みたいページを正面に向け、「このページを要約」を押してください。")
            .foregroundStyle(.secondary)
          BookPreview(camera: camera)
          HStack {
            Label(wearables.registrationState == .registered ? "登録済み" : "未登録", systemImage: "eyeglasses")
            Spacer()
            Text(camera.isStreaming ? "映像受信中" : camera.isPaused ? "一時停止中" : "映像停止中")
          }
          .font(.caption)

          if wearables.registrationState != .registered {
            Button("メガネを接続") { wearables.connectGlasses() }
              .disabled(wearables.registrationState == .registering)
          } else {
            HStack {
              Button(camera.hasSession ? "接続を終了" : "接続を開始") {
                reader.stop()
                if camera.hasSession { camera.endSession() } else { camera.startSession() }
              }
              .disabled(camera.isBusy || (!camera.hasSession && !camera.hasActiveDevice))
              Button(camera.hasStream ? "映像を停止" : "映像を開始") {
                reader.stop()
                if camera.hasStream { camera.stopStreaming() }
                else { Task { await camera.startStreaming() } }
              }
              .disabled(camera.isBusy || !camera.isSessionActive)
            }
          }

          if wearables.requiresFirmwareUpdate {
            Button("メガネのファームウェアを更新") { Task { await wearables.openFirmwareUpdate() } }
          }
          if camera.showError {
            Text(camera.errorMessage).foregroundStyle(.red)
            Button("メガネ側アプリの更新を確認") { Task { await wearables.openDATGlassesAppUpdate() } }
          }
          if wearables.showError { Text(wearables.errorMessage).foregroundStyle(.red) }
          if let callbackError { Text(callbackError).foregroundStyle(.red) }

          Stepper("要約は\(limit)文字以内", value: $limit, in: 50...1000, step: 50)
            .disabled(reader.isWorking)
          Button {
            guard camera.isStreaming, let image = camera.currentVideoFrame else { return }
            reader.read(image: image, limit: limit)
          } label: {
            Label(reader.isWorking ? "読み取り・要約中…" : "このページを要約", systemImage: "book.closed")
              .frame(maxWidth: .infinity)
          }
          .buttonStyle(.borderedProminent)
          .controlSize(.large)
          .disabled(reader.isWorking || !camera.isStreaming || camera.currentVideoFrame == nil)

          if reader.isWorking {
            HStack {
              ProgressView()
              Button("キャンセル") { reader.stop() }
            }
          }
          if let error = reader.errorMessage { Text(error).foregroundStyle(.red) }
          if !reader.summary.isEmpty {
            VStack(alignment: .leading, spacing: 12) {
              Text("要約 · \(reader.summary.count)文字").font(.headline)
              Text(reader.summary).textSelection(.enabled)
              HStack {
                Button("もう一度聴く") { reader.play() }
                Button("読み上げ停止") { reader.stop() }
              }
            }
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 16))
          }
          Text("要約時の画像をOpenAIへ送信します。画像や本文はアプリからファイル保存しません。音声はiPhoneで生成し、接続中の音声出力先に再生します。メガネから聴く場合は音声出力先を確認してください。")
            .font(.footnote).foregroundStyle(.secondary)
        }
        .padding()
      }
      .navigationTitle("Meta Book Reader")
      .navigationBarTitleDisplayMode(.inline)
      .toolbar {
        Button { showSettings = true } label: { Image(systemName: "gearshape") }
          .accessibilityLabel("設定")
      }
      .sheet(isPresented: $showSettings) { ReaderSettingsView() }
      .alert("カメラへのアクセス", isPresented: $camera.showCameraPermissionRedirectConfirm) {
        Button("続ける") { Task { await camera.confirmCameraPermissionRedirect() } }
        Button("キャンセル", role: .cancel) {}
      } message: {
        Text("Meta AIアプリでカメラの利用を許可したあと、このアプリに戻ります。")
      }
      .onOpenURL { url in
        guard URLComponents(url: url, resolvingAgainstBaseURL: false)?
          .queryItems?.contains(where: { $0.name == "metaWearablesAction" }) == true else { return }
        Task {
          do { _ = try await Wearables.shared.handleUrl(url) }
          catch { callbackError = error.localizedDescription }
        }
      }
      .onChange(of: scenePhase) { _, phase in
        if phase == .background { reader.stop() }
      }
      .onChange(of: camera.isStreaming) { _, streaming in
        if !streaming { reader.stop() }
      }
      .onDisappear { reader.stop(); camera.endSession() }
    }
  }
}

private struct BookPreview: View {
  let camera: CameraViewModel
  var body: some View {
    ZStack {
      Color.black
      if let frame = camera.currentVideoFrame {
        Image(uiImage: frame).resizable().scaledToFit()
      } else {
        VStack(spacing: 8) {
          Image(systemName: "book").font(.largeTitle)
          Text("メガネを接続して映像を開始")
        }.foregroundStyle(.white)
      }
      if camera.isBusy { ProgressView().tint(.white) }
    }
    .frame(height: 340)
    .clipShape(RoundedRectangle(cornerRadius: 20))
    .accessibilityLabel("メガネのカメラ映像")
  }
}

private struct ReaderSettingsView: View {
  @Environment(\.dismiss) private var dismiss
  @State private var apiKey = KeychainStore.read()
  @State private var saveError: String?
  var body: some View {
    NavigationStack {
      Form {
        Section("OpenAI API") {
          SecureField("APIキー", text: $apiKey)
            .textInputAutocapitalization(.never)
            .autocorrectionDisabled()
          Text("ご自身のAPIキーを端末のKeychainに保存します。OpenAI APIの利用料金が発生します。")
            .font(.footnote)
          Text("画像解析：gpt-4.1-mini／読み上げ：iPhoneの日本語音声")
            .font(.footnote)
        }
        if let saveError { Text(saveError).foregroundStyle(.red) }
      }
      .navigationTitle("設定")
      .toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("閉じる") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("保存") {
            do { try KeychainStore.save(apiKey); dismiss() }
            catch { saveError = error.localizedDescription }
          }
        }
      }
    }
  }
}
